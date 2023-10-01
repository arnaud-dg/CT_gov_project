import pandas as pd
import streamlit as st
import snowflake.connector
import altair as alt

# Importing function
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

# Drop-down list of the sidebar
df_disease = fetch_data("select $1 from available_diseases")
selected_disease = st.sidebar.selectbox("Please select a disease :", df_disease['$1'].tolist())
st.sidebar.write("Vous avez choisi : ", selected_disease)

df_countries = fetch_data("SELECT * FROM studies_countries")
df_countries = df_countries[df_countries['DISEASE'] == selected_disease]

st.title('🏥 World map of clinical studies 🧑‍⚕️')

st.dataframe(df_countries)
