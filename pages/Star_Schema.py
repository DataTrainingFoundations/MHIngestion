import streamlit as st
from sqlalchemy import text
from graphviz import Digraph

st.title("Star Schema Diagram ")

conn = st.connection("mysql", type="sql")

# Fact and dimension tables
fact_table = "fact_mental_health"
dim_tables = ["category_dim", "time_dim", "confidence_dim"]
tables = [fact_table] + dim_tables

# ---------- FUNCTIONS ----------
def get_columns(table):
    query = text(f"""
        SELECT column_name, data_type, column_key
        FROM information_schema.columns
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)
    with conn.session as s:
        return s.execute(query).fetchall()

def get_foreign_keys():
    query = text("""
        SELECT
            table_name,
            column_name,
            referenced_table_name,
            referenced_column_name
        FROM information_schema.key_column_usage
        WHERE referenced_table_name IS NOT NULL
    """)
    with conn.session as s:
        return s.execute(query).fetchall()

# ---------- BUILD GRAPH ----------
graph = Digraph("StarSchema", format="png")
graph.attr(splines="ortho", nodesep="1", ranksep="1", fontsize="10")

# --- Add fact table in center ---
cols = get_columns(fact_table)
label = f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0'>"
label += f"<TR><TD BGCOLOR='lightcoral'><B>{fact_table}</B></TD></TR>"
for col, dtype, key in cols:
    if key == "PRI":
        label += f"<TR><TD ALIGN='LEFT'>🔑 {col} : {dtype}</TD></TR>"
    else:
        label += f"<TR><TD ALIGN='LEFT'>{col} : {dtype}</TD></TR>"
label += "</TABLE>>"
graph.node(fact_table, label=label, shape="plain")

# --- Add dimension tables in the same rank around fact table ---
with graph.subgraph() as s:
    s.attr(rank="same")
    for dim in dim_tables:
        cols = get_columns(dim)
        label = f"<<TABLE BORDER='1' CELLBORDER='1' CELLSPACING='0'>"
        label += f"<TR><TD BGCOLOR='lightblue'><B>{dim}</B></TD></TR>"
        for col, dtype, key in cols:
            if key == "PRI":
                label += f"<TR><TD ALIGN='LEFT'>🔑 {col} : {dtype}</TD></TR>"
            else:
                label += f"<TR><TD ALIGN='LEFT'>{col} : {dtype}</TD></TR>"
        label += "</TABLE>>"
        s.node(dim, label=label, shape="plain")

# --- Add FK edges with labels ---
fks = get_foreign_keys()
for table, column, ref_table, ref_col in fks:
    if table == fact_table and ref_table in dim_tables:
        graph.edge(
            fact_table,
            ref_table,
            label=f"{column} → {ref_col}",
            fontsize="10",
            fontcolor="black",
            arrowhead="normal",
            arrowsize="1"
        )

# ---------- DISPLAY ----------
st.graphviz_chart(graph)

# ---------- OPTIONAL: show raw table structures ----------
if st.checkbox("Show raw table structures"):
    for table in tables:
        st.subheader(table)
        st.table(get_columns(table))