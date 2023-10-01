import streamlit as st
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
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

df_nlp = fetch_data("SELECT * FROM master_data")
df_nlp = df_nlp[df_nlp['DISEASE'] == selected_disease]
df_nlp['Text_field'] = df_nlp['OFFICIALTITLE'] + df_nlp['BRIEFSUMMARY'] + df_nlp['DETAILEDDESCRIPTION']

st.header('Text analysis of the Study Description')
st.dataframe(df_nlp)

# Create some sample text
text = ' '.join(df_nlp['Text_field'])
text = text.split(" ")

# Create and generate a word cloud image:
wordcloud = WordCloud().generate(text)

# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
st.pyplot()
