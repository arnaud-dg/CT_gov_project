import pandas as pd
import streamlit as st
import snowflake.connector
import altair as alt
import plotly.express as px
import leafmap.foliumap as leafmap

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

df_countries = fetch_data("SELECT * FROM country_map")
df_countries = df_countries[df_countries['DISEASE'] == selected_disease]
df_sites = fetch_data("SELECT * FROM studies_sites")
df_sites = df_sites[df_sites['LATITUDE'].isna() == False]
df_sites = df_sites[df_sites['LONGITUDE'].isna() == False]
#df_sites['LATITUDE'] = df_sites['LATITUDE'].astype(float)
#df_sites['LONGITUDE'] = df_sites['LONGITUDE'].astype(float)
df_sites['VALUE'] = 1
df_sites = df_sites[df_sites['DISEASE'] == selected_disease]

st.title('🏥 World map of clinical studies 🧑‍⚕️')

st.dataframe(df_sites)
st.echo(df_sites.info())


tab1, tab2 = st.tabs(["Worldmap by countries", "Sites Heatmap"])

with tab1:
    fig = px.choropleth(df_countries, locations="COUNTRY_CODE_ISO",
                        color="NUMBER_STUDIES", # lifeExp is a column of gapminder
                        hover_name="LOCATIONCOUNTRY", # column to add to hover information
                        color_continuous_scale=px.colors.sequential.Plasma)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig)

with tab2:
    m = leafmap.Map(center=[0, 0], zoom=2, tiles="stamentoner")
    m.add_heatmap(
        df_sites,
        latitude="LATITUDE",
        longitude="LONGITUDE",
        value="VALUE",
        radius=5,
    )
    m.to_streamlit(height=700)
