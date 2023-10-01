import pandas as pd
import streamlit as st
import snowflake.connector
import altair as alt
import plotly.express as px

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

df_delay = fetch_data("SELECT * FROM study_delay")
df_delay = df_delay[df_delay['DISEASE'] == selected_disease]

st.header('Focus on classical delays')
st.dataframe(df_delay)
col1, col2 = st.st.columns(2)

with col1:
  fig1 = px.histogram(df_delay, x="total_bill", y="tip", color="sex",
                   marginal="box", # or violin, rug
                   hover_data=df.columns)
  st.plotly(fig1)
with col2:
