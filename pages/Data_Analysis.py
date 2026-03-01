import base64
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Visualization Lab", layout="wide")
st.title("Visualization Lab")
st.caption("Visualize mental health data.")

# --- Load your DataFrame ---
conn = st.connection("mysql", type="sql")
df = conn.query("SELECT * FROM mental_health", ttl=0)

if df.empty:
    st.warning("Database is empty.")
    st.stop()

st.subheader("Mental Health Data Preview")
st.dataframe(df.head(20), use_container_width=True)

# ------------------------
# === Line Plots by Subcategory ===
indicator_col = df.columns[0]         # indicator column
subcategory_col = "subcategory"       # e.g., By Sex, By Education, etc.
time_col = "time_period_start_date"   # time period start date (keep as string)
value_col = "value"                   # numeric value column

# --- Select indicator constant ---
selected_indicator = st.selectbox(
    "Select Indicator",
    df[indicator_col].unique()
)

# Filter by selected indicator
df_indicator = df[df[indicator_col] == selected_indicator]

# --- MULTI-SELECT for subcategories, nothing pre-selected ---
subcategories_all = df_indicator[subcategory_col].unique().tolist()
selected_subcategories = st.multiselect(
    "Select subcategories to plot",
    options=subcategories_all,
    default=[],  # nothing pre-selected
    help="Select one or more subcategories to display on the graph."
)

# --- Only show the plot if the user selected at least one subcategory ---
if selected_subcategories:
    df_filtered = df_indicator[df_indicator[subcategory_col].isin(selected_subcategories)].copy()

    # Keep x-axis exactly as in the table
    df_filtered[time_col] = df_filtered[time_col].astype(str)

    fig, ax = plt.subplots(figsize=(12,6))

    sns.lineplot(
        data=df_filtered,
        x=time_col,            
        y=value_col,           
        hue=subcategory_col,   # separate line per subcategory
        marker=None,           
        ax=ax
    )

    ax.set_xlabel("Time Period Start Date")
    ax.set_ylabel("Value")
    ax.grid(alpha=0.2)

    # Slightly diagonal x-axis labels for readability
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")  

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

else:
    st.info("Select at least one subcategory to see the chart.")