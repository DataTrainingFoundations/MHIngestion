import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt

# Title
st.title("Mental Health Visualization")

# Button to reload data
if st.button("Reload Data"):
    st.experimental_rerun()  # reruns the script

# Load data (CSV, database, etc.)
PROJECT_ROOT = Path(__file__).resolve().parent
data_path = PROJECT_ROOT / "data" / "valid_data.csv"
df = pd.read_csv(data_path)

# Show table
st.dataframe(df)



