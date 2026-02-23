import base64
import io
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualization Lab", layout="wide")
st.title("Visualization Lab")
st.caption("Visualize mental health data.")

# --- Load your DataFrame ---
# replace with your actual MySQL connection if needed
conn = st.connection("mysql", type="sql")
df = conn.query("SELECT * FROM mental_health")

if df.empty:
    st.warning("Database is empty.")
    st.stop()

st.write("Preview (first 20 rows)")
st.dataframe(df.head(20), use_container_width=True)

# --- Detect numeric columns for Y-axis ---
numeric_cols = df.select_dtypes(include="number").columns.tolist()
all_cols = df.columns.tolist()

# Sidebar for X/Y selection
x_axis = st.selectbox("X-axis column", options=all_cols, index=0)
y_axis = st.selectbox("Y-axis column (numeric)", options=numeric_cols, index=0)

# Chart type selection
chart_type = st.selectbox(
    "Chart type",
    ["Bar", "Line", "Scatter", "Histogram", "Box", "Cumulative Sum"]
)

# Downsampling
step_size = st.slider(
    "Sample every N rows",
    min_value=1, max_value=50, value=1, step=1,
    help="Downsample large datasets to reduce visual clutter."
)
df_sampled = df.iloc[::step_size].copy()

# --- Wrap long labels for readability ---
def wrap_text(val, width=25):
    val = str(val)
    return "\n".join([val[i:i+width] for i in range(0, len(val), width)])

df_sampled[x_axis] = df_sampled[x_axis].apply(wrap_text)

# --- Plot ---
fig, ax = plt.subplots(figsize=(10,5))

if chart_type == "Bar":
    means = df_sampled.groupby(x_axis)[y_axis].mean()
    ax.bar(means.index, means.values)
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.tick_params(axis="x", rotation=0)

elif chart_type == "Line":
    ax.plot(df_sampled[x_axis], df_sampled[y_axis], marker='o')
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.tick_params(axis="x", rotation=0)

elif chart_type == "Scatter":
    ax.scatter(df_sampled[x_axis], df_sampled[y_axis])
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.tick_params(axis="x", rotation=0)

elif chart_type == "Histogram":
    ax.hist(df_sampled[y_axis], bins=20, alpha=0.85, edgecolor="white")
    ax.set_xlabel(y_axis)
    ax.set_ylabel("Count")

elif chart_type == "Box":
    ax.boxplot(df_sampled[y_axis], labels=[x_axis])
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)

else:  # Cumulative sum
    ax.plot(df_sampled[x_axis], df_sampled[y_axis].cumsum())
    ax.set_xlabel(x_axis)
    ax.set_ylabel(f"Cumulative {y_axis}")

ax.grid(alpha=0.2)
st.pyplot(fig, use_container_width=True)

# --- Download PNG ---
png_buffer = io.BytesIO()
fig.savefig(png_buffer, format="png", dpi=150, bbox_inches="tight")
png_bytes = png_buffer.getvalue()
st.download_button("Download PNG", png_bytes, file_name="chart.png", mime="image/png")

# --- Download HTML ---
img_b64 = base64.b64encode(png_bytes).decode("utf-8")
html = f"""<!doctype html>
<html><body><img src="data:image/png;base64,{img_b64}" /></body></html>""".encode("utf-8")
st.download_button("Download HTML", html, file_name="chart.html", mime="text/html")