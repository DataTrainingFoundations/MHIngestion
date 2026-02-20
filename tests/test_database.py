import streamlit as st
import sqlalchemy as sa
import pytest


@pytest.fixture(scope="session")
def database_engine():
    conn = st.connection("mysql", type="sql")
    engine = conn.engine

    yield engine
    

def test_connection(database_engine):

    inspector = sa.inspect(database_engine)
    columns_info = inspector.get_columns("mental_health")
    column_list = [c.get('name') for c in columns_info]

    list_of_required_sql_columns = ['indicator', 'category', 'state', 'subcategory', 'phase', 'time_period', 'time_period_label', 'time_period_start_date', 'time_period_end_date', 'value', 'lowci', 'highci', 'confidence_interval', 'quartile_range']

    doesDatabaseHaveRequiredColumns = set(list_of_required_sql_columns).issubset(set(column_list))

    assert doesDatabaseHaveRequiredColumns