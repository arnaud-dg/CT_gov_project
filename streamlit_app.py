import requests, io
import pandas as pd
import streamlit as st
import altair as alt

# Send and retrieve HTTP (REST) request
disease = "parkinson"
min_value = 1
max_value = 5
url = "https://clinicaltrials.gov/api/query/study_fields?expr=" + disease + "&min_rnk=" + str(min_value) + "&max_rnk=" + str(max_value) + "&fmt=csv"

res = requests.get(url).content

# Extract contents, skip CSV header (first 10 lines), to dataframe
data = pd.read_csv(io.StringIO(res.decode("utf-8")), skiprows=10).fillna(0)

streamlit.header("Tableau de données")
streamlit.dataframe(data)
