import pandas as pd
import streamlit as st
import snowflake.connector
import altair as alt
from streamlit_extras.app_logo import add_logo
from streamlit_extras.metric_cards import style_metric_cards

# Layout of the main page
st.set_page_config(layout="wide")
add_logo("gallery/transparent_logo_DATA_BOOST_2.png", height=300)

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

st.title('🏥 Clinical Trials .Gov Explorer 🧑‍⚕️')

# Dashboard - Big numbers & Metrics
df_metrics = fetch_data("SELECT * FROM studies_count")
df_metrics = df_metrics[df_metrics['DISEASE'] == selected_disease]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total number of studies", df_metrics['COUNT'].sum())
col2.metric("On-going Clinical studies", df_metrics[df_metrics['SIMPLIFIEDSTATUS'] == 'On-going']['COUNT'].sum())
col3.metric("Completed Clinical studies", df_metrics[df_metrics['SIMPLIFIEDSTATUS'] == 'Closed']['COUNT'].sum())
col4.metric("Number of lines", df_metrics[df_metrics['SIMPLIFIEDSTATUS'] == 'Unknown']['COUNT'].sum())
style_metric_cards(background_color = '#FFF', border_size_px = 1, border_color = '#CCC', border_radius_px = 5, border_left_color = '#AED2FF', box_shadow = True)


