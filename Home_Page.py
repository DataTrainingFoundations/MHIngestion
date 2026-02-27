import streamlit as st
from main import *

st.set_page_config(page_title="Project Home", layout="wide")
st.title("Mental Health & Unemployment Dashboard")

conn = st.connection("mysql", type="sql")

# --- load Button ---
if "force_reload" not in st.session_state:
    st.session_state.force_reload = False
if st.button("Load Data"):
    main()
    st.session_state.force_reload = True

# --- Reload Button ---
if "force_reload" not in st.session_state:
    st.session_state.force_reload = False

if st.button("Reload All Data"):
    st.session_state.force_reload = True

# --- Load Data ---
if st.session_state.force_reload:
    # ttl=0 forces fresh query (no cache)
    df_mh = conn.query("SELECT * FROM mental_health", ttl=0)
    df_ut = conn.query(
        """
        SELECT *
        FROM unemployment
        """,
        ttl=0
    )
    # reset trigger
    st.session_state.force_reload = False
else:
    df_mh = conn.query("SELECT * FROM mental_health")
    df_ut = conn.query(
        """
        SELECT *
        FROM unemployment
        """
    )

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
st.dataframe(df_mh, use_container_width=True)

st.subheader("Unemployment Data")
st.dataframe(df_ut, use_container_width=True)