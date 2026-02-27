import pytest
import pandas as pd
import numpy as np

from ingestion.Reader import read_data
from ingestion.Validator import retrieve_data
from ingestion.Cleaner import clean_data

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "indicator": [" Received Counseling or Therapy, Last 4 Weeks "],
        "group": [" By Sex "],
        "state": [" United States "],
        "subgroup": [" Male "],
        "phase": ["2"],
        "time_period": ["15"],
        "time_period_label": [" Sep 16 - Sep 28, 2020 "],
        "time_period_start_date": ["09/16/2020"],
        "time_period_end_date": ["09/28/2020"],
        "value": ["6.9"],
        "lowci": ["6.5"],
        "highci": ["7.3"],
        "confidence_interval": ["6.5 - 7.3"],
        "quartile_range": ["6.5 - 7.5"],
        "suppression_flag": ["0"]
    })


def test_remove_duplicates(sample_df):
    df = pd.concat([sample_df, sample_df])  # duplicate row
    cleaned = clean_data(df)

    assert len(cleaned) == 1

def test_string_trimming(sample_df):
    cleaned = clean_data(sample_df)

    assert cleaned.loc[0, "indicator"] == "Received Counseling or Therapy, Last 4 Weeks"
    assert cleaned.loc[0, "group"] == "By Sex"
    assert cleaned.loc[0, "state"] == "United States"

def test_numeric_conversion(sample_df):
    cleaned = clean_data(sample_df)

    assert cleaned.loc[0, "value"] == 6.9
    assert cleaned.loc[0, "lowci"] == 6.5
    assert cleaned.loc[0, "highci"] == 7.3

def test_invalid_numeric_to_none(sample_df):
    sample_df["value"] = ["not_a_number"]
    sample_df["lowci"] = ["bad"]
    sample_df["highci"] = ["wrong"]

    cleaned = clean_data(sample_df)

    assert cleaned.loc[0, "value"] is None
    assert cleaned.loc[0, "lowci"] is None
    assert cleaned.loc[0, "highci"] is None

def test_time_period_numeric(sample_df):
    cleaned = clean_data(sample_df)

    assert cleaned.loc[0, "time_period"] == 15

def test_datetime_conversion(sample_df):
    cleaned = clean_data(sample_df)

    assert isinstance(cleaned.loc[0, "time_period_start_date"], pd.Timestamp)
    assert isinstance(cleaned.loc[0, "time_period_end_date"], pd.Timestamp)

def test_invalid_datetime_to_none(sample_df):
    sample_df["time_period_start_date"] = ["bad_date"]

    cleaned = clean_data(sample_df)

    assert cleaned.loc[0, "time_period_start_date"] is None

def test_text_columns_string_dtype(sample_df):
    cleaned = clean_data(sample_df)

    text_cols = [
        "indicator", "group", "state", "subgroup",
        "time_period_label", "confidence_interval", "quartile_range"
    ]

    for col in text_cols:
        assert cleaned[col].dtype.name in ["string", "object"]

def test_nan_replaced_with_none(sample_df):
    sample_df["phase"] = [np.nan]

    cleaned = clean_data(sample_df)

    assert cleaned.loc[0, "phase"] is None