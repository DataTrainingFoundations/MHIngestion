from ingestion.Reader import read_data
from ingestion.Validator import retrieve_data

NDATAROWS = 10404
DATA_FILE = "data/Mental_Health_DB.csv"
SINGLE_VALID_ROW_FILE = "tests/test_files/single_valid_row.csv"

def areNoRowsAccepted(df):
    assert(df[0].shape[0] == 0)

def doesChangeCauseRejection(variableName, variableValue):
    df = read_data("tests/test_files/single_valid_row.csv")
    df.loc[0, variableName] = variableValue
    valid_df, rejected_df = retrieve_data(df)
    isChangedDataRejected = rejected_df.shape[0] == 1
    return isChangedDataRejected

def test_all_data_loaded():
    assert read_data(DATA_FILE).shape[0]  == NDATAROWS

def test_successful_validation(): 
    df = read_data(SINGLE_VALID_ROW_FILE)
    valid_df, rejected_df = retrieve_data(df)
    assert valid_df.shape[0] == 1

def test_removed_column():
    df = read_data(DATA_FILE)
    df.drop("Group", axis=1, inplace=True)
    areNoRowsAccepted(retrieve_data(df))

def test_validator_rejects_suppression_flag():
    assert doesChangeCauseRejection("Suppression Flag", 1)

def test_validator_rejects_phase_equal_negative_one():
    assert doesChangeCauseRejection("Phase", -1)

if __name__ == "__main__":
    test_all_data_loaded()
    test_successful_validation()
    