import os
import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

FIPS_TO_STATE = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming"
}


def clean_data_api(df):
    logger.info("Starting data cleaning step")
    
    original_rows = len(df)

    # --- Remove duplicates ---
    df = df.drop_duplicates()
    logger.debug(f"Removed {original_rows - len(df)} duplicate rows")

    # --- Trim strings ---
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # --- Enforce numeric types ---
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    logger.debug(f"Converted column value to numeric")
    
    # --- Enforce datetime ---
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    logger.debug(f"Converted column year to numeric")
        #creates a month column and sets it = to period without the M
    df["month"] = (df["period"].astype(str).str.strip().str.replace("M", "", regex=False))
    df["month"] = pd.to_numeric(df["month"], errors="coerce")
    logger.debug(f"Created temporary column month and converted it to numeric")

        #creates date column which takes the year and month and converts it to datetime
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-" +
        df["month"].astype(str).str.zfill(2) + "-01",errors="coerce")
    logger.debug(f"Created column date and converted it to datetime")

    # --- Extract state from series_id ---
    df["series_id"] = df["series_id"].astype("string")
    logger.debug(f"Converted series_id to string")
    df["state_fips"] = df["series_id"].str.slice(5, 7)
    logger.debug(f"Created temporary column state_fips")
    #creates permanent column state which will replace series id
    df["state"] = df["state_fips"].map(FIPS_TO_STATE)

    #validator for the mapping
    missing_states = df["state"].isna().sum()
    if missing_states > 0:
        logger.warning(f"There are {missing_states} rows with unmapped FIPS codes")

    # --- Drops Unneccessary Columns ---
    df.drop(columns=['series_id', 'state_fips', 'year', 'month', 'period_name'], inplace=True)
    logger.debug(f"dropped columns series_id, state_fips, year, month, and period_name")

    #if the dataframe has the rejected columns cleans them
    if'rejection_reason' in df.columns:
        df['rejection_reason'] = df['rejection_reason'].astype("string")
        logger.debug(f"Converted rejection_reason to string")
        #reindexs with rejection reason
        df = df.reindex(columns=["state", "date", "value", "rejection_reason"])
    else:
        #reindexs without rejection reason
        df = df.reindex(columns=["state", "date", "value",])



    logger.info(f"Completed data cleaning.")
    df = df.replace({pd.NA: None, np.nan: None})
 
    return df