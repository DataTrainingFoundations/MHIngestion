import pandas as pd
import logging
from .Reader import read_data

# Logger for the Ingestion 
logger = logging.getLogger(__name__)

def retrieve_data(df):

    # Normalize column names so your REQUIRED_FIELDS match
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    logger.info(f"Normalized columns: {list(df.columns)}")

    # These fields cant be null
    REQUIRED_FIELDS = [
        "indicator", "group", "state", "subgroup", "phase",
        "time_period", "time_period_label",
        "time_period_start_date", "time_period_end_date"
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

    # looks for suppression = 1 and phase = -1
    suppression = (df.get("suppression_flag", pd.Series(0, index=df.index)) == 1.0)
    phase = (df.get("phase", pd.Series("", index=df.index)).astype(str).str.strip() == "-1")

    # Rejected if any reject condition
    rejected = missing_required | suppression | phase

    rejected_df = df[rejected].copy()

    #anything that doesn't meet the rejected conditions becomes valid
    valid_df = df[~rejected].copy()
    # Remove the suppression flag column as it is no longer necessary
    valid_df.drop(columns=['suppression_flag'], inplace=True)
    
    # Add rejection reasons (nice for stg_rejects)
    # Priority order: missing required > suppression > phase
    def reason_for_row(row) -> str:
        missing = [c for c in REQUIRED_FIELDS if c not in row.index or pd.isna(row[c]) or str(row[c]).strip() == ""]
        if missing:
            return f"missing required field(s): {', '.join(missing)}"
        if row.get("suppression_flag", 0) == 1.0:
            return "suppression flag = 1"
        if str(row.get("phase", "")).strip() == "-1":
            return "phase = -1"
        return "unknown"
    
    rejected_df["rejection_reason"] = rejected_df.apply(reason_for_row, axis=1)

    #logs succesfully created valid and rejected data frames
    logger.info(f"Successfully validated {len(valid_df.index)} rows")
    logger.info(f"Rejected {len(rejected_df.index)} rows")

    return valid_df, rejected_df
    
