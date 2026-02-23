import logging
import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import streamlit as st

connection = None
#database configuration
logging.basicConfig(filename='logs/dblog.log', filemode="a",\
    format="%(process)d - %(asctime)s - %(name)s - %(message)s", \
        datefmt= "%d-%b-%y %H:%M:%S",level = logging.DEBUG)
logger = logging.getLogger("DBlogger")
def start_unemployment_DB():
    try:
        global connection
        connection = st.connection('mysql', type='sql')
        with connection.session as s:
            s.execute(text("""CREATE TABLE IF NOT EXISTS unemployment (state_fips CHAR(2) NOT NULL, state VARCHAR(50) NOT NULL, date DATE NOT NULL, \
                            unemployment_rate DECIMAL(5,2), UNIQUE KEY uq_state_date (state_fips, date))"""))
            s.execute(text("""CREATE TABLE IF NOT EXISTS unemployment_rejected (state_fips CHAR(2) NOT NULL, state VARCHAR(50) NOT NULL, date DATE NOT NULL, \
                            unemployment_rate DECIMAL(5,2), UNIQUE KEY uq_state_date (state_fips, date), rejection_reason TEXT)"""))
    except Exception as err:
        logger.error(f"An error has occurred during connection: {err}")

def insert_valid_unemployment_data(df):
    data_to_insert = df.to_dict(orient='records')
    insert_query = text("""INSERT INTO unemployment (state_fips, state, date, unemployment_rate) \
                        VALUES (:state_fips, :state, :date, :value)""")
    try:
        with connection.session as s:
           s.execute(insert_query, data_to_insert) 
           s.commit()
        logger.info(f"Succesfully inserted {len(data_to_insert)} rows into database")
    except Exception as err:
        logger.error(f"Error occurred during data insertion: {err}")

def insert_rejected_data(df):
    data_to_insert = df.to_dict(orient='records')
    insert_query = text("""INSERT INTO unemployment_rejected (state_fips, state, date, unemployment_rate, rejection_reason) \
                        VALUES (:state_fips, :state, :date, :value, :rejection_reason)""")
    try:
        with connection.session as s:
           s.execute(insert_query, data_to_insert) 
           s.commit()
        logger.info(f"Succesfully inserted {len(data_to_insert)} rows into rejected database")
    except Exception as err:
        logger.error(f"Error occurred during data insertion: {err}")

def close_connection():
    try:
        connection.close()
        logger.info("Successfully closed DB connection")
    except Exception as err:
        logger.error(f"Error occurred when closing the connection: {err}")

def get_max_unemployment_month():
    # Return MAX(date) from unemployment table
    try:
        with connection.session as s:
            row = s.execute(text("SELECT MAX(date) FROM unemployment")).fetchone()
            return row[0]  # None if empty
    except Exception as err:
        logger.error(f"Error fetching MAX(date): {err}")
        raise

def upsert_valid_unemployment_data(df: pd.DataFrame):
    #UPSERT valid rows into unemployment table using UNIQUE(state_fips, date)
    if df.empty:
        logger.info("df empty. nothing to upsert.")
        return
    data_to_insert = df.to_dict(orient="records")
    upsert_sql = text("""INSERT INTO unemployment (state_fips, state, date, unemployment_rate)
                      VALUES (:state_fips, :state, :date, :value)
                      ON DUPLICATE KEY UPDATE
                      unemployment_rate = VALUES(unemployment_rate)""")
    try:
        with connection.session as s:
            s.execute(upsert_sql, data_to_insert)
            s.commit()
        logger.info(f"Upserted/updated {len(data_to_insert)} rows into unemployment")
    except Exception as err:
        logger.error(f"Error occurred during unemployment upsert: {err}")
        raise