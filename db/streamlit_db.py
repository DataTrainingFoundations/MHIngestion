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
            s.execute(text("""CREATE TABLE mental_health (indicator TEXT NOT NULL, category TEXT NOT NULL, state TEXT NOT NULL, \
                            subcategory TEXT NOT NULL, phase NUMERIC, time_period INT, time_period_label TEXT NOT NULL, time_period_start_date DATE NOT NULL,\
                            time_period_end_date DATE NOT NULL, value NUMERIC, lowci NUMERIC, highci NUMERIC, confidence_interval TEXT, quartile_range TEXT)"""))
            s.execute(text("""CREATE TABLE mental_health_rejected (indicator TEXT, category TEXT, \
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

def read_valid_data():
    df = connection.query("SELECT * FROM mental_health")
    return df

def close_connection():
    try:
        connection.close()
        logger.info("Successfully closed DB connection")
    except Exception as err:
        logger.error(f"Error occurred when closing the connection: {err}")

def starify():
    with connection.session as s:
        s.execute(text("DROP TABLE IF EXISTS fact_mental_health"))
        s.execute(text("DROP TABLE IF EXISTS category_dim"))
        s.execute(text("DROP TABLE IF EXISTS time_dim"))
        s.execute(text("DROP TABLE IF EXISTS confidence_dim"))
        s.execute(text("""CREATE TABLE category_dim (category_key INT AUTO_INCREMENT PRIMARY KEY, \
                            category TEXT, subcategory TEXT)"""))
        s.execute(text("""CREATE TABLE time_dim (time_key INT AUTO_INCREMENT PRIMARY KEY, \
                            phase NUMERIC, time_period INT, time_period_label TEXT, time_period_start_date DATE, \
                            time_period_end_date DATE)"""))
        s.execute(text("""CREATE TABLE confidence_dim (confidence_key INT AUTO_INCREMENT PRIMARY KEY, \
                            lowci NUMERIC, highci NUMERIC, confidence_interval TEXT, quartile_range TEXT)"""))
        s.execute(text("""CREATE TABLE fact_mental_health (fact_id INT AUTO_INCREMENT PRIMARY KEY, \
                            category_key INT, time_key INT, confidence_key INT, indicator TEXT, value NUMERIC, \
                            FOREIGN KEY (category_key) REFERENCES category_dim(category_key), \
                            FOREIGN KEY (time_key) REFERENCES time_dim(time_key), \
                            FOREIGN KEY (confidence_key) REFERENCES confidence_dim(confidence_key))"""))
        s.execute(text("""INSERT INTO category_dim (category, subcategory) \
                            SELECT DISTINCT category, subcategory FROM mental_health"""))
        s.execute(text("""INSERT INTO time_dim (phase, time_period, time_period_label, time_period_start_date, \
                            time_period_end_date) \
                            SELECT DISTINCT phase, time_period, time_period_label, time_period_start_date, \
                            time_period_end_date FROM mental_health"""))
        s.execute(text("""INSERT INTO confidence_dim (lowci, highci, confidence_interval, quartile_range) \
                            SELECT DISTINCT lowci, highci, confidence_interval, quartile_range FROM mental_health"""))
        s.execute(text("""INSERT INTO fact_mental_health (category_key, time_key, confidence_key, indicator, value) \
                            SELECT ca.category_key, t.time_key, co.confidence_key, m.indicator, m.value \
                            FROM mental_health m \
                            JOIN category_dim ca ON (m.category = ca.category AND m.subcategory = ca.subcategory) \
                            JOIN time_dim t ON (m.time_period_start_date = t.time_period_start_date AND \
                            m.time_period_end_date = t.time_period_end_date) \
                            JOIN confidence_dim co ON (m.lowci = co.lowci AND m.highci = co.highci)"""))
        s.commit()