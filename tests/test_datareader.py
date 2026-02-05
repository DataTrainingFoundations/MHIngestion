from ingestion.Reader import read_data
from ingestion.Validator import retrieve_data

NDATAROWS = 10404

def test_all_data_loaded():
    assert read_data("data/Raw Data/Mental_Health_DB.csv").shape[0]  == NDATAROWS

def test_successful_validation():
    valid_df, rejected_df = retrieve_data()

    assert valid_df.shape[0] + rejected_df.shape[0] == (NDATAROWS)

if __name__ == "__main__":
    test_all_data_loaded()
    test_successful_validation()