import pandas as pd
import streamlit as st
import snowflake.connector
import altair as alt
import plotly.express as px
import leafmap.foliumap as leafmap
import geopandas as gpd

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

st.dataframe(df_countries)

st.title('🏥 World map of clinical studies 🧑‍⚕️')
tab1, tab2, tab3 = st.tabs(["Worldmap by countries", "Sites heatmap", "Sites detailed view"])

gdf = gpd.read_file('shapefiles/world-administrative-boundaries/world-administrative-boundaries.shp')

mymap = folium.Map(location=[19.0649070739746, 73.1308670043945], zoom_start=2, tiles=None)
choropleth = folium.Choropleth(
    geo_data=gdf,
    data=df,
    key_on='feature.properties.iso3',
    columns=['Country Name', '2020'], #the first one is the 'index' which needs to be connected with the 'key_on' property of  the geo_data
    name = 'GDP per capita (Constant USD 2015 )',
    fill_color='YlGn', fill_opacity=0.7, line_opacity=0.5).add_to(mymap)

with tab1:
    m1 = leafmap.Map(center=[0, 0], zoom=2, tiles="None")
    folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(my1)
    choropleth = folium.Choropleth(
    geo_data=gdf,
    data=df_countries,
    key_on='feature.properties.name',
    columns=['Country_code_iso', '2020'], #the first one is the 'index' which needs to be connected with the 'key_on' property of  the geo_data
    name = 'Number of on-going clinical studies',
    fill_color='YlGn', fill_opacity=0.7, line_opacity=0.5).add_to(m1)
    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['name'], labels=True))
    m1.to_streamlit(height=700)

with tab2:
    m2 = leafmap.Map(center=[0, 0], zoom=2, tiles="Stamen Terrain")
    m2.add_heatmap(
        df_sites,
        latitude="LATITUDE",
        longitude="LONGITUDE",
        value="VALUE",
        radius=10,
    )
    m2.to_streamlit(height=700)

with tab3:
    m3 = leafmap.Map(center=[0, 0], zoom=2, tiles="Stamen Terrain")
    m3.add_points_from_xy(
        df_sites,
        y="LATITUDE",
        x="LONGITUDE"
    )
    m3.to_streamlit(height=700)
