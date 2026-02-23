from ingestion.Reader import DataReader

def test_all_data_loaded():
    datareader = DataReader()
    assert len(datareader.read_data()) == 10404

if __name__ == "__main__":
    test_all_data_loaded()
