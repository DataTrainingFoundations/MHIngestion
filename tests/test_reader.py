<<<<<<< HEAD
from ingestion.Reader import read_data

def test_all_data_loaded(data_path):
    assert len(read_data(data_path)) == 10404

if __name__ == "__main__":
    data_path: str = "data/Raw Data/Mental_Health_DB.csv"
=======
from ingestion.Reader import DataReader

def test_all_data_loaded():
    datareader = DataReader()
    assert len(datareader.read_data()) == 10404

if __name__ == "__main__":
>>>>>>> 31b9628171278a5484e5161c8c4024f88c78214f
    test_all_data_loaded()
