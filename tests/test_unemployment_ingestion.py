from api_ingestion import *

from pathlib import Path


def test_is_api_call_working():

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    print(PROJECT_ROOT)
    data_path = PROJECT_ROOT / "data" / "unemployment_data_seed.json"
    
    df = read_json(data_path)

    print(df.head())

    columns_to_check = ["series_id", "year", "period", "period_name", "value"]

    does_data_contain_required_columns = set(columns_to_check).issubset(df.columns)
    is_data_not_empty = df.shape[0] != 0

    print(does_data_contain_required_columns)
    print(is_data_not_empty)

    assert does_data_contain_required_columns and is_data_not_empty
