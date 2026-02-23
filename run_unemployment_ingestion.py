import os
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from api_ingestion import *
from db import streamlit_api_db

import pandas as pd

# BLS typically updates on the first friday of every month, so run the CRON
# on the second monday, so even accounting for delays I should be able to pull
# up to date data.

logger = logging.getLogger(__name__)

#ingests BLS unemployment database for the newest month and the year before checking for updates
def run_unemployment_ingestion():
    #confirms credentials
    load_dotenv()
    api_key = os.getenv("BLS_API_KEY")
    if not api_key:
        raise ValueError("BLS_API_KEY missing in env/.env")

    # Connect to DB
    streamlit_api_db.start_unemployment_DB()

    # Get most recent date SQL QUERY
    recent_date = streamlit_api_db.get_max_unemployment_month()
    

    # Calculate start year and end year
    if recent_date is None:
        target_month = date(2020, 1, 1)   # seed month
    else:
        target_month = recent_date + relativedelta(months=1)

    # Normalize to first of month
    target_month = date(target_month.year, target_month.month, 1)

    start_month = target_month - relativedelta(months=11)
    end_month = target_month

    # Get series ids
    STATE_FIPS = [
    "01","02","04","05","06","08","09","10","12","13",
    "15","16","17","18","19","20","21","22","23","24",
    "25","26","27","28","29","30","31","32","33","34",
    "35","36","37","38","39","40","41","42","44","45",
    "46","47","48","49","50","51","53","54","55","56"
    ]  
    series_ids = [f"LAUST{fips}0000000000003" for fips in STATE_FIPS]

    # Get result from api
    try:
        df_raw = fetch_bls_timeseries(
            series_ids=series_ids,
            start_year=start_month.year,
            end_year=end_month.year,
            api_key=BLS_API_KEY
        )

        # Validate and Clean results
        valid, reject = retrieve_data_api(df_raw)
        valid = clean_data_api(valid)
        reject = clean_data_api(reject)

        #Applies a window to ensure only next month and last 11 months are upserted
        valid_window = valid[(valid["date"] >= pd.Timestamp(start_month)) & (valid["date"] <= pd.Timestamp(end_month))].copy()

        # SQL UPSERT 
        streamlit_api_db.upsert_valid_unemployment_data(valid_window)

        # close database
        streamlit_api_db.close_connection_api()
    except Exception as e:
        logger.exception("BLS API Extraction Failed")

if __name__ == "__main__":
    run_unemployment_ingestion()