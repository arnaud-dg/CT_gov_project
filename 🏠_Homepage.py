import pandas as pd
import streamlit as st
import snowflake.connector
import altair as alt
from streamlit_extras.app_logo import add_logo
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras import extra

# Layout of the main page
st.set_page_config(layout="wide")
add_logo("gallery/transparent_logo_DATA_BOOST.png", height=300)

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
st.sidebar.write("""This web application, made with Streamlit, is a personal project I undertook to practice with AWS, Snowflake, SQL, and Python.
The aim of this application is to provide a synthetic analysis of past and ongoing clinical studies for a given pathology.
To limit the data volume, only a few pathologies have been set up. The data comes from the Clinicaltrials.gov API.""")
st.sidebar.write("""Enjoy the journey! :sunglasses:""")
st.sidebar.markdown("""---""")
selected_disease = st.sidebar.selectbox("Please select a pathology:", df_disease['$1'].tolist())

st.title('🏥 Clinical Trials .Gov Explorer 🧑‍⚕️')

# Dashboard - Big numbers & Metrics
df_metrics = fetch_data("SELECT * FROM studies_count")
df_metrics = df_metrics[df_metrics['DISEASE'] == selected_disease]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total number of studies", df_metrics['COUNT'].sum())
col2.metric("On-going Clinical studies", df_metrics[df_metrics['SIMPLIFIEDSTATUS'] == 'On-going']['COUNT'].sum())
col3.metric("Completed Clinical studies", df_metrics[df_metrics['SIMPLIFIEDSTATUS'] == 'Closed']['COUNT'].sum())
col4.metric("Number of lines", df_metrics[df_metrics['SIMPLIFIEDSTATUS'] == 'Unknown']['COUNT'].sum())
#style_metric_cards(background_color='#FFF', border_size_px=1, border_color='#CCC', border_radius_px=5, border_left_color="#9AD8E1")
style_metric_cards()

# Dashboard - Plotly charts
# Study count (per phase)
df_chart1 = fetch_data("SELECT * FROM studies_count")
df_chart1 = df_chart1[df_chart1['DISEASE'] == selected_disease]

st.dataframe(df_chart1)

# Enrolment count (per phase)
df_chart2 = fetch_data("SELECT * FROM studies_count")
df_chart2 = df_chart2[df_chart2['DISEASE'] == selected_disease]

# Pie chart by therapeutic family
df_chart3 = fetch_data("SELECT * FROM studies_count")
df_chart3 = df_chart3[df_chart3['DISEASE'] == selected_disease]

# Pie chart by status
df_chart4 = fetch_data("SELECT * FROM studies_count")
df_chart4 = df_chart4[df_chart4['DISEASE'] == selected_disease]
