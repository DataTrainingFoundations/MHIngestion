import pandas as pd
import logging

# Logger for the Ingestion 
logger = logging.getLogger(__name__)

def retrieve_data_api(df):

    # Normalize column names 
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    logger.info(f"Normalized columns: {list(df.columns)}")

    # These fields cant be null
    REQUIRED_FIELDS = [
        'series_id', 'year', 'period', 'period_name', 'value'
    ]

    def is_null(series: pd.Series) -> pd.Series:
        # True if NaN OR place-holder string
        return series.isna() | series.astype(str).str.strip().str.lower().isin(["", "na", "n/a", "null", "none"])

    # looks for required field missing
    missing_required = pd.Series(False, index=df.index)
    for col in REQUIRED_FIELDS:
        if col not in df.columns:
            # If a required column is missing entirely, reject ALL rows
            missing_required |= True
        else:
            missing_required |= is_null(df[col])

    # looks for Period = M13
    period = (df.get("period", pd.Series(0, index=df.index)) == "M13")
    
    # Rejected if any reject condition
    rejected = missing_required | period

    rejected_df = df[rejected].copy()

    #anything that doesn't meet the rejected conditions becomes valid
    valid_df = df[~rejected].copy()
    
    # Adds rejection reasons
    def reason_for_row(row) -> str:
        missing = [c for c in REQUIRED_FIELDS if c not in row.index or pd.isna(row[c]) or str(row[c]).strip() == ""]
        if missing:
            return f"missing required field(s): {', '.join(missing)}"
        if row.get("period", 0) == "M13":
            return "Period = M13"
        return "unknown"
    
    rejected_df["rejection_reason"] = rejected_df.apply(reason_for_row, axis=1)

    #logs succesfully created valid and rejected data frames
    logger.info(f"Successfully validated {len(valid_df.index)} rows")
    logger.info(f"Rejected {len(rejected_df.index)} rows")

    return valid_df, rejected_df