import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "data", "Raw Data", "Mental_Health_DB.csv")

print("Trying path:", CSV_PATH)
print("Exists?", os.path.exists(CSV_PATH))

df = pd.read_csv(CSV_PATH)
print(df.dtypes)

def clean_data(df):
    # --- Remove duplicates ---
    df = df.drop_duplicates()

    # --- Trim strings ---
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # --- Enforce numeric types ---
    numeric_cols = ["Phase", "Value", "LowCI", "HighCI"]#idk about the last three
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Enforce int type ---
    df["Time Period"] = pd.to_numeric(df["Time Period"], errors="coerce").astype("Int64")

    # --- Enforce datetime ---
    df["Time Period Start Date"] = pd.to_datetime(df["Time Period Start Date"], errors="coerce")
    df["Time Period End Date"] = pd.to_datetime(df["Time Period End Date"], errors="coerce")

    # --- Normalize text columns ---
    text_cols = [
        "Indicator", "Group", "State", "Subgroup",
        "Time Period Label", "Confidence Interval", "Quartile Range"
    ]
    for col in text_cols:
        df[col] = df[col].astype("string")
    
    print("\nAfter type enforcement:")
    print(df.dtypes)


    return df
df_clean = clean_data(df)

