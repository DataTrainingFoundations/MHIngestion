import streamlit as st
import pandas as pd

st.set_page_config(page_title="Project Home", layout="wide")
st.title("Mental Health & Unemployment Dashboard")

# --- Reload Button ---
if "reload_trigger" not in st.session_state:
    st.session_state.reload_trigger = 0

if st.button("Reload Data"):
    st.session_state.reload_trigger += 1

_ = st.session_state.reload_trigger  # dummy variable to trigger rerun

# --- Load Data ---
conn = st.connection("mysql", type="sql")
df_mh = conn.query("SELECT * FROM mental_health")
df_ut = conn.query("SELECT * FROM unemployment")

# --- Project Overview ---
st.header("Project Overview")
st.markdown(
    """
    This project focused on building an ETL pipeline from two sources:  
    1. **CDC's Mental Health Survey dataset** 
    2. **Bureau of Labor Statistics (BLS) API**  

    The system was designed to reliably ingest and store these datasets in a relational database,  
    while supporting recurring updates to the BLS's unemployment data.  

    After ingestion, the structured data was analyzed to identify trends and relationships  
    between mental health indicators and unemployment statistics.
    """
)

# --- Data Preview ---
st.header("Data Preview")

st.subheader("Mental Health Data")
st.dataframe(df_mh.head(20), use_container_width=True)

st.subheader("Unemployment Data")
st.dataframe(df_ut.head(20), use_container_width=True)