import pytest
import pandas as pd
import numpy as np
from api_ingestion import *

@pytest.fixture
def base_data():
    return {
        "series_id": ["LAUST010000000000003", "LAUST060000000000003"],
        "year": [2022, 2022],
        "period": ["M12", "M11"],
        "period_name": ["December", "November"],
        "value": [2.0, 2.2]
    }

def test_remove_duplicates(base_data):
    df = pd.DataFrame(base_data)
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    cleaned_df = clean_data_api(df)
    assert len(cleaned_df) == 2

def test_string_trimming(base_data):
    base_data["series_id"] = ["  LAUST010000000000003  ", "LAUST060000000000003"]
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    assert cleaned_df["state_fips"].iloc[0] == "01"

def test_fips_mapping(base_data):
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    assert cleaned_df.loc[cleaned_df["state_fips"] == "01", "state"].iloc[0] == "Alabama"
    assert cleaned_df.loc[cleaned_df["state_fips"] == "06", "state"].iloc[0] == "California"

def test_date_creation(base_data):
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    assert cleaned_df["date"].iloc[0] == pd.Timestamp("2022-12-01")
    assert cleaned_df["date"].iloc[1] == pd.Timestamp("2022-11-01")

def test_columns_dropped(base_data):
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    dropped_cols = ['series_id', 'year', 'month', 'period_name']
    for col in dropped_cols:
        assert col not in cleaned_df.columns

def test_value_numeric_conversion(base_data):
    base_data["value"] = ["5.5", "invalid_str"]
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    assert cleaned_df["value"].iloc[0] == 5.5
    assert cleaned_df["value"].iloc[1] is None

def test_column_order_standard(base_data):
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    expected_order = ["state_fips", "state", "date", "value"]
    assert list(cleaned_df.columns) == expected_order

def test_column_order_with_rejection(base_data):
    base_data["rejection_reason"] = ["Reason A", "Reason B"]
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    expected_order = ["state_fips", "state", "date", "value", "rejection_reason"]
    assert list(cleaned_df.columns) == expected_order

def test_unmapped_fips(base_data):
    base_data["series_id"] = ["LAUST990000000000003", "LAUST010000000000003"]
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    assert cleaned_df.loc[cleaned_df["state_fips"] == "99", "state"].iloc[0] is None

def test_nan_to_none_conversion(base_data):
    base_data["period"] = ["M13", "M12"]
    df = pd.DataFrame(base_data)
    cleaned_df = clean_data_api(df)
    assert cleaned_df["date"].iloc[0] is None