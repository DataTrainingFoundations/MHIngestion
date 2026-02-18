import os
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from api_ingestion import *
from db import streamlit_api_db

import pandas as pd

logger = logging.getLogger(__name__)

#scrapes BLS unemployment database for the newest month and the year before checking for updates
def run_unemployment_scraper():
    #confirms credentials
    load_dotenv()
    api_key = os.getenv("BLS_API_KEY")
    if not api_key:
        raise ValueError("BLS_API_KEY missing in env/.env")

    # --- Connect to DB ---

    #--- Get most recent date SQL QUERY ---
    recent_date = date()

    #calculate start year and end year
    next_month = recent_date.month + 1
    if(next_month > 12):
        end_date = recent_date.year + 1
    else:
        end_date = recent_date.year
    start_date = end_date-1

    #get series ids
    STATE_FIPS = [
    "01","02","04","05","06","08","09","10","12","13",
    "15","16","17","18","19","20","21","22","23","24",
    "25","26","27","28","29","30","31","32","33","34",
    "35","36","37","38","39","40","41","42","44","45",
    "46","47","48","49","50","51","53","54","55","56"
    ]  
    series_ids = [f"LAUST{fips}0000000000003" for fips in STATE_FIPS]

    # get result from api
    try:
        df_raw = fetch_bls_timeseries(
            series_ids=series_ids,
            start_year=start_date,
            end_year=end_date,
            api_key=BLS_API_KEY
        )

        valid, reject = retrieve_data_api(df_raw)
        valid = clean_data_api(valid)
        reject = clean_data_api(reject)

        # --- SQL UPSERT here ---
        upsert_sql = """
                    INSERT INTO stg_unemployment (state_fips, state, date, unemployment_rate)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    unemployment_rate = VALUES(unemployment_rate)
                    """ 

    except Exception as e:
        logger.exception("BLS API Extraction Failed")

