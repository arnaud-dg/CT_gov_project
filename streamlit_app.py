import pandas as pd
import streamlit as st
import snowflake.connector

my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
my_cur = my_cnx.cursor()
my_cur.execute("select * from available_diseases")
my_data_row = my_cur.fetchone()

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "Please select a disease :", my_data_row
)

st.title('🦜🔗 Quickstart App')
