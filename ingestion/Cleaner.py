import os
import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

def clean_data(df):
    logger.info("Starting data cleaning step")
    
    original_rows = len(df)

    # --- Remove duplicates ---
    df = df.drop_duplicates()
    logger.debug(f"Removed {original_rows - len(df)} duplicate rows")

    # --- Trim strings ---
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # --- Enforce numeric types ---
    numeric_cols = ["phase", "value", "lowci", "highci"]#idk about the last three
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        logger.debug(f"Converted column '{col}' to numeric")

    # --- Enforce int type ---
    df["time_period"] = pd.to_numeric(df["time_period"], errors="coerce")
    logger.debug("Converted 'time_period' to nullable Int64")

    # --- Enforce datetime ---
    df["time_period_start_date"] = pd.to_datetime(df["time_period_start_date"], errors="coerce")
    logger.debug(f"Converted 'time_period_start_date' to datetime")
    df["time_period_end_date"] = pd.to_datetime(df["time_period_end_date"], errors="coerce")
    logger.debug(f"Converted 'time_period_end_date' to datetime")

    # --- Normalize text columns ---
    text_cols = [
        "indicator", "group", "state", "subgroup",
        "time_period_label", "confidence_interval", "quartile_range"
    ]
    for col in text_cols:
        df[col] = df[col].astype("string")
        logger.debug(f"Converted '{col}' to string")

    #if the dataframe has the rejected columns cleans them
    if'rejection_reason' in df.columns:
        df['suppression_flag'] = pd.to_numeric(df['suppression_flag'], errors="coerce")
        logger.debug(f"Converted suppression_flag to numeric")
        df['rejection_reason'] = df['rejection_reason'].astype("string")
        logger.debug(f"Converted rejection_reason to string")



    logger.info(f"Completed data cleaning.")
    df = df.replace({pd.NA: None, np.nan: None})
 
    return df
