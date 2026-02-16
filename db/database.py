# import logging
# import mysql.connector
# import pandas as pd
# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine

# load_dotenv(r"db\credentials.env")
# connection = None
# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
# db_host = os.getenv("DB_HOST")
# print(db_host)
# #database configuration
# logging.basicConfig(filename='logs/dblog.log', filemode="a",\
#     format="%(process)d - %(asctime)s - %(name)s - %(message)s", \
#         datefmt= "%d-%b-%y %H:%M:%S",level = logging.DEBUG)
# logger = logging.getLogger("DBlogger")
# def start_DB():
#     try:
#         global connection
#         connection = mysql.connector.connect(user=db_user, password=db_password, host=db_host, database='mental_health_db')
#         if connection.is_connected():
#             logger.info("Successfully connected to database")
#             with connection.cursor() as cursor:
#                 cursor.execute("CREATE DATABASE IF NOT EXISTS mental_health_db")
#                 cursor.execute("USE mental_health_db")
#                 cursor.execute("""CREATE TABLE IF NOT EXISTS mental_health (indicator TEXT NOT NULL, category TEXT NOT NULL, state TEXT NOT NULL, \
#                                subcategory TEXT NOT NULL, phase NUMERIC, time_period INT, time_period_label TEXT NOT NULL, time_period_start_date DATE NOT NULL,\
#                                 time_period_end_date DATE NOT NULL, value NUMERIC, lowci NUMERIC, highci NUMERIC, confidence_interval TEXT, quartile_range TEXT)""")
#                 cursor.execute("""CREATE TABLE IF NOT EXISTS mental_health_rejected (indicator TEXT, category TEXT, \
#                                state TEXT, subcategory TEXT, phase NUMERIC, time_period INT, time_period_label TEXT, \
#                                time_period_start_date DATE, time_period_end_date DATE, value NUMERIC, lowci NUMERIC, highci NUMERIC,\
#                                 confidence_interval TEXT, quartile_range TEXT, suppression_flag NUMERIC, rejection_reason TEXT)""")
#         else:
#             logger.warning("Failed to connect to DB. Check credentials and DB status and try again.")
#     except mysql.connector.Error as err:
#         logger.error(f"An error has occurred during connection: {err}")

# def insert_valid_data(df):
#     data_to_insert = [tuple(row) for row in df.values]
#     insert_query = """INSERT INTO mental_health (indicator, category, state, \
#                                subcategory, phase, time_period, time_period_label, time_period_start_date,\
#                                 time_period_end_date, value, lowci, highci, confidence_interval, quartile_range) VALUES (%s, %s, %s, \
#                                %s, %s, %s, %s, %s,\
#                                 %s, %s, %s, %s, %s, %s)"""
#     try:
#         connection.cursor().executemany(insert_query, data_to_insert)
#         connection.commit()
#         logger.info(f"Succesfully inserted {len(data_to_insert)} rows into database")
#     except mysql.connector.Error as err:
#         logger.error(f"Error occurred during data insertion: {err}")

# def insert_rejected_data(df):
#     data_to_insert = [tuple(row) for row in df.values]
#     insert_query = f"""INSERT INTO mental_health_rejected (indicator, category, state , \
#                                subcategory, phase, time_period, time_period_label, time_period_start_date,\
#                                 time_period_end_date, value, lowci, highci, confidence_interval, quartile_range,\
#                                       suppression_flag, rejection_reason) VALUES (%s, %s, %s, \
#                                %s, %s, %s, %s, %s,\
#                                 %s, %s, %s, %s, %s, %s, %s, %s)"""
#     try:
#         connection.cursor().executemany(insert_query, data_to_insert)
#         connection.commit()
#         logger.info(f"Succesfully inserted {len(data_to_insert)} rows into rejected database")
#     except mysql.connector.Error as err:
#         logger.error(f"Error occurred during data insertion: {err}")

# def close_connection():
#     try:
#         connection.close()
#         logger.info("Successfully closed DB connection")
#     except mysql.connector.Error as err:
#         logger.error(f"Error occurred when closing the connection: {err}")