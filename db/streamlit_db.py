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
def start_DB():
    try:
        global connection
        connection = st.connection('mysql', type='sql')
        with connection.session as s:
            s.execute(text("DROP TABLE IF EXISTS mental_health"))
            s.execute(text("DROP TABLE IF EXISTS mental_health_rejected"))
            s.execute(text("""CREATE TABLE IF NOT EXISTS mental_health (indicator TEXT NOT NULL, category TEXT NOT NULL, state TEXT NOT NULL, \
                            subcategory TEXT NOT NULL, phase NUMERIC, time_period INT, time_period_label TEXT NOT NULL, time_period_start_date DATE NOT NULL,\
                            time_period_end_date DATE NOT NULL, value NUMERIC, lowci NUMERIC, highci NUMERIC, confidence_interval TEXT, quartile_range TEXT)"""))
            s.execute(text("""CREATE TABLE IF NOT EXISTS mental_health_rejected (indicator TEXT, category TEXT, \
                            state TEXT, subcategory TEXT, phase NUMERIC, time_period INT, time_period_label TEXT, \
                            time_period_start_date DATE, time_period_end_date DATE, value NUMERIC, lowci NUMERIC, highci NUMERIC,\
                            confidence_interval TEXT, quartile_range TEXT, suppression_flag NUMERIC, rejection_reason TEXT)"""))
            logger.info("Successfully connected to database")
    except Exception as err:
        logger.error(f"An error has occurred during connection: {err}")

def insert_valid_data(df):
    data_to_insert = df.to_dict(orient='records')
    insert_query = text("""INSERT INTO mental_health (indicator, category, state, \
                               subcategory, phase, time_period, time_period_label, time_period_start_date,\
                                time_period_end_date, value, lowci, highci, confidence_interval, quartile_range) VALUES (:indicator, :group, :state, \
                               :subgroup, :phase, :time_period, :time_period_label, :time_period_start_date,\
                                :time_period_end_date, :value, :lowci, :highci, :confidence_interval, :quartile_range)""")
    try:
        with connection.session as s:
           s.execute(insert_query, data_to_insert) 
           s.commit()
        logger.info(f"Succesfully inserted {len(data_to_insert)} rows into database")
    except Exception as err:
        logger.error(f"Error occurred during data insertion: {err}")

def insert_rejected_data(df):
    data_to_insert = df.to_dict(orient='records')
    insert_query = text("""INSERT INTO mental_health_rejected (indicator, category, state , \
                               subcategory, phase, time_period, time_period_label, time_period_start_date,\
                                time_period_end_date, value, lowci, highci, confidence_interval, quartile_range,\
                                suppression_flag, rejection_reason) VALUES (:indicator, :group, :state , \
                               :subgroup, :phase, :time_period, :time_period_label, :time_period_start_date,\
                                :time_period_end_date, :value, :lowci, :highci, :confidence_interval, :quartile_range,\
                                      :suppression_flag, :rejection_reason)""")
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