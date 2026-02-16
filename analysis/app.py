import streamlit as st
import pandas as pd
import altair as alt

# Title
st.title("Mental Health Visualization")

# Button to reload data
if st.button("Reload Data"):
    st.experimental_rerun()  # reruns the script

# Load data (CSV, database, etc.)
df = pd.read_csv("/Users/rashmiwagde/Documents/Developer/MHIngestion/data/valid_data.csv")

# Show table
st.dataframe(df)



