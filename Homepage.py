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

# Dashboard - Big numbers & Metrics
df_metrics = fetch_data("SELECT * FROM studies_count")
df_metrics = df_metrics[df_metrics['disease'] == seleccted_disease]
st.title('🏥 Clinical Trials .Gov Explorer 🧑‍⚕️')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total number of studies", df_metrics['Count'].sum())
col2.metric("On-going Clinical studies", df_metrics[df_metrics['simplifiedstatus'] == 'On-going'])
col3.metric("Completed Clinical studies", df_metrics[df_metrics['simplifiedstatus'] == 'Closed'])
col4.metric("Number of lines", df_metrics[df_metrics['simplifiedstatus'] == 'Unknown'])

st.dataframe(df_metrics)
