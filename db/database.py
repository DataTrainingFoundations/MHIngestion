import sqlite3
import mysql.connector
import sys

#database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'testuser',
    'password': 'password'
}

#attempt to connect to the MySQL database
try:
    connection = mysql.connector.connect(**DB_CONFIG)
    if connection.is_connected():
        print("Successful connection achieved")
        with connection.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS mental_health (indicator TEXT, category TEXT, state TEXT, subcategory TEXT, Phase TEXT, time_period REAL, time_period_label TEXT, time_period_start_date TEXT, time_period_end_date TEXT, value REAL, lowci REAL, highci REAL, confidence_interval TEXT, quartile_range TEXT)""")
        connection.close()
except mysql.connector.Error as err:
    print(f"An error has occurred during connection: {err}")
    sys.exit(1)


# conn = sqlite3.connect('testDB.db')
# c = conn.cursor()

# c.execute("""CREATE TABLE IF NOT EXISTS mental_health (indicator TEXT, category TEXT, state TEXT, subcategory TEXT, Phase TEXT, time_period REAL, time_period_label TEXT, time_period_start_date TEXT, time_period_end_date TEXT, value REAL, lowci REAL, highci REAL, confidence_interval TEXT, quartile_range TEXT)""")