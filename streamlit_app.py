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
    disease_list.append(row[0])
    
# Using object notation
add_selectbox = st.sidebar.selectbox(
    "Please select a disease :", disease_list
)

st.title('🦜🔗 Quickstart App')
sf.dataframe(my_data_row)
