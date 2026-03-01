import pytest
import pandas as pd
import numpy as np
from api_ingestion import *  

@pytest.fixture
def base_data():
    return pd.DataFrame({
        'series_id': ['ID001'],
        'year': [2022],
        'period': ['M01'],
        'period_name': ['January'],
        'value': [5.5]
    })

def test_m13_rejection(base_data):
    m13_row = pd.DataFrame({
        'series_id': ['ID002'], 'year': [2022], 'period': ['M13'], 
        'period_name': ['Annual'], 'value': [10.0]
    })
    df = pd.concat([base_data, m13_row], ignore_index=True)
    
    valid_df, rejected_df = retrieve_data_api(df)
    
    assert len(valid_df) == 1
    assert len(rejected_df) == 1
    assert rejected_df.iloc[0]['rejection_reason'] == "Period = M13"

def test_missing_required_column(base_data):
    invalid_df = base_data.drop(columns=['value'])
    
    valid_df, rejected_df = retrieve_data_api(invalid_df)
    
    assert len(valid_df) == 0
    assert len(rejected_df) == 1
    assert "missing required field(s): value" in rejected_df.iloc[0]['rejection_reason']

