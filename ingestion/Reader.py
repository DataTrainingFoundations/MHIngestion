import pandas as pd
import logging

def read_data(data_path):
    try:
        # data_path: str = "data/Raw Data/Mental_Health_DB.csv"
        # takes a csv and turns it into a pandas dataframe
        df = pd.read_csv(data_path)

        # logs successful reading
        # ("read " + len(records) + f" rows from source file {self.data_path}") 

        return df
            
            
    except:
        print("something went wrong")






