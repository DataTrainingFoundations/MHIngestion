import pandas as pd

class DataReader():

    def __init__(self):
        self.data_path: str = "data/Raw Data/Mental_Health_DB.csv"
    
    def read_data(self) -> list[dict]:
        try:
            # takes a csv and turns it into a pandas dataframe
            df = pd.read_csv(self.data_path)
            # turns that dataframe into a list of dicts
            records = df.to_dict(orient="records")

            # logs successful reading
            # ("read " + len(records) + f" rows from source file {self.data_path}") 

            return records
            
            
        except:
            print("something went wrong")




