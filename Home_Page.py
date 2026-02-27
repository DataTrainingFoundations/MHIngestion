import streamlit as st

st.set_page_config(page_title="Project Home", layout="wide")
st.title("Mental Health & Unemployment Dashboard")

conn = st.connection("mysql", type="sql")

# --- Reload Button ---
if st.button("Reload Unemployment Data"):
    st.session_state.force_reload = True

# --- Load Mental Health Data (normal cached query) ---
df_mh = conn.query("SELECT * FROM mental_health")

# --- Load Unemployment Data ---
if st.session_state.get("force_reload", False):
    # ttl=0 forces fresh query (no cache)
    df_ut = conn.query("""
        SELECT * 
        FROM unemployment
        ORDER BY date DESC
    """, ttl=0)

    # reset trigger
    st.session_state.force_reload = False
else:
    df_ut = conn.query("""
        SELECT * 
        FROM unemployment
        ORDER BY date DESC
    """)

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