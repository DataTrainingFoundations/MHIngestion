import logging
from ingestion import *
# from db import *
from db.streamlit_db import *
from pathlib import Path
import mysql.connector

def main():
    # Logger for the Ingestion 
    Path("logs").mkdir(exist_ok=True)

    logging.basicConfig(
        filename="logs/ingestion.log",
        filemode="a",
        format="%(process)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=logging.DEBUG
    )

    logger = logging.getLogger("main")
    logger.info("Ingestion pipeline starting")

    # our mental health db
    PROJECT_ROOT = Path(__file__).resolve().parent
    data_path = PROJECT_ROOT / "data" / "Mental_Health_DB.csv"
    #turns the csv into a dataframe
    df = read_data(data_path)
    #takes the dataframe and turns it into a valid and a rejected dataframe
    
    valid, rejected = retrieve_data(df)
    #cleans the valid data to be stored int he database
    valid = clean_data(valid)
    rejected = clean_data(rejected)
    # print(valid[valid['phase'].isna()])
    start_DB()
    insert_valid_data(valid)
    insert_rejected_data(rejected)
    close_connection()
    #loads valid into database
    #loader method goes here


if __name__ == "__main__":
    main()