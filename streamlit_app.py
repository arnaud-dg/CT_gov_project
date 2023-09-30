import pandas as pd
import streamlit as st
import snowflake.connector

my_cnx = snowflake.connector.connect(**st.secrets["snowflake"])
my_cur = my_cnx.cursor()
my_cur.execute("select $1 from available_diseases")
df = my_cur.fetchone()

# Initialize connection.
conn = st.experimental_connection('snowpark')

# Load the table as a dataframe using the Snowpark Session.
@st.cache_data
def load_table(table_name):
    with conn.safe_session() as session:
        return session.table(table_name).to_pandas()

df = load_table("available_diseases")

disease_list = []
for row in df.itertuples():
    disease_list.append(row)
    
# Using object notation
add_selectbox = st.sidebar.selectbox(
    "Please select a disease :", disease_list
)

st.title('🦜🔗 Quickstart App')
sf.dataframe(my_data_row)
