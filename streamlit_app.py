import pandas as pd
import streamlit as st
import snowflake.connector

def fetch_data(SQL_query):
    # Connection to snowflake and cursor creation
    conn = snowflake.connector.connect(**st.secrets["snowflake"])
    cur = conn.cursor()
    cur.execute(SQL_query)
    # Loading Data into a DataFrame
    df = pd.DataFrame.from_records(iter(cur), columns=[x[0] for x in cur.description])
    # Close the connection
    cur.close()
    conn.close()
    return df

df = fetch_data("select $1 from available_diseases")
disease_list = []
for row in df.itertuples():
    disease_list.append(row[1])
    
# Using object notation
add_selectbox = st.sidebar.selectbox(
    "Please select a disease :", disease_list
)

data = fetch_data("select NCTID from MASTER_DATA WHERE disease = 'parkinson' LIMIT 10")

st.title('🦜🔗 Quickstart App')
st.dataframe(data)
