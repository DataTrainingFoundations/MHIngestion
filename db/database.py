import pandas as pd
import mysql.connector
import sys

#database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234'
}
def retrieve_data(filepath):
    # read data from file into pandas dataframe
    df = pd.read_csv(filepath)
    
    # Fill in NaN suppression flag values since we cannot remove rows containing 1.0 as their suppression flag without having a value to compare to
    df['Suppression Flag'] = df['Suppression Flag'].fillna(0.0)
    
    # Removes all rows with a suppression flag of 1.0, indicating the data should be suppressed
    filtered_df = df[df['Suppression Flag'] != 1.0]

    # Removes all rows containing a Phase of -1 since all rows containing this lack most usable data
    filtered_df = filtered_df[filtered_df['Phase'] != '-1']

    # Remove the suppression flag column as it is no longer necessary
    filtered_df.drop(columns=['Suppression Flag'], inplace=True)
    
    return filtered_df
    
retrieve_data(r"data\Raw Data\Mental_Health_DB.csv")
#attempt to connect to the MySQL database
try:
    connection = mysql.connector.connect(**DB_CONFIG)
    if connection.is_connected():
        print("Successful connection achieved")
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS mental_health_db")
            cursor.execute("USE mental_health_db")
            cursor.execute("""CREATE TABLE IF NOT EXISTS mental_health (indicator TEXT, category TEXT, state TEXT, subcategory TEXT, Phase TEXT, time_period REAL, time_period_label TEXT, time_period_start_date TEXT, time_period_end_date TEXT, value REAL, lowci REAL, highci REAL, confidence_interval TEXT, quartile_range TEXT)""")
        connection.close()
except mysql.connector.Error as err:
    print(f"An error has occurred during connection: {err}")
    sys.exit(1)


# conn = sqlite3.connect('testDB.db')
# c = conn.cursor()

# c.execute("""CREATE TABLE IF NOT EXISTS mental_health (indicator TEXT, category TEXT, state TEXT, subcategory TEXT, Phase TEXT, time_period REAL, time_period_label TEXT, time_period_start_date TEXT, time_period_end_date TEXT, value REAL, lowci REAL, highci REAL, confidence_interval TEXT, quartile_range TEXT)""")