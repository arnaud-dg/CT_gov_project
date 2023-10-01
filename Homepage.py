import pandas as pd
import streamlit as st
import snowflake.connector
import altair as alt

st.markdown("""
    <style>
        .reportview-container .main .block-container {
            max-width: 90%;
        }
    </style>
""", unsafe_allow_html=True)

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


query = "select NCTID from MASTER_DATA WHERE disease = '" + selected_disease + "' LIMIT 10"
data = fetch_data(query)

st.title('🏥 Clinical Trials .Gov Explorer 🧑‍⚕️')
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total number of studies", fetch_data("SELECT count(*) FROM studies_count WHERE disease = '" + selected_disease + "'").iloc[0, 0])
col2.metric("On-going Clinical studies", fetch_data("SELECT count(*) FROM studies_count WHERE disease = '" + selected_disease + "' AND simplifiedstatus = 'On-going'").iloc[0, 0])
col3.metric("Completed Clinical studies", fetch_data("SELECT count(*) FROM studies_count WHERE disease = '" + selected_disease + "' AND simplifiedstatus = 'Closed'").iloc[0, 0])
col4.metric("Number of lines", fetch_data("SELECT count(*) FROM studies_count WHERE disease = '" + selected_disease + "' AND simplifiedstatus = 'Unknown'").iloc[0, 0])

