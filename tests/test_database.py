import streamlit as st
import sqlalchemy as sa
import sqlalchemy.orm
import pytest

NDATAROWS = 10404

@pytest.fixture(scope="session")
def database_engine():
    conn = st.connection("mysql", type="sql")
    engine = conn.engine

    yield engine
    
@pytest.fixture(scope="session")
def tables(database_engine):
    metadata = sa.MetaData()
    metadata.reflect(bind=database_engine)
    
    return metadata.tables

@pytest.fixture(scope="function")
def db_session(database_engine):
    Session = sa.orm.sessionmaker(bind=database_engine)
    session = Session()

    yield session

    session.close()    


def test_connection(database_engine):

    inspector = sa.inspect(database_engine)
    columns_info = inspector.get_columns("mental_health")
    column_list = [c.get('name') for c in columns_info]

    list_of_required_sql_columns = ['indicator', 'category', 'state', 'subcategory', 'phase', 'time_period', 'time_period_label', 'time_period_start_date', 'time_period_end_date', 'value', 'lowci', 'highci', 'confidence_interval', 'quartile_range']

    doesDatabaseHaveRequiredColumns = set(list_of_required_sql_columns).issubset(set(column_list))

    assert doesDatabaseHaveRequiredColumns

def helper_get_row_count_from_table(db_session, table):
    get_row_count_query = sa.select(sa.func.count()).select_from(table)
    return db_session.execute(get_row_count_query).scalar_one()


def test_correct_database_row_count(db_session, tables):

    mental_health_row_count = helper_get_row_count_from_table(db_session, tables['mental_health'])
    mental_health_rejected_row_count = helper_get_row_count_from_table(db_session, tables['mental_health_rejected'])
    total_rows = mental_health_row_count + mental_health_rejected_row_count

    assert total_rows == NDATAROWS