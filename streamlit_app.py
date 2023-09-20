import requests, io
import pandas as pd
import streamlit as st
import altair as alt

# Send and retrieve HTTP (REST) request
url =

'request_url'

res = requests.get(url).content

# Extract contents, skip CSV header (first 10 lines), to dataframe
data = pd.read_csv(io.StringIO(res.decode("utf-8")), skiprows=10).fillna(0)

request_url:
https://clinicaltrials.gov/api/query/study_fields
?expr=multiple+sclerosis
&fields=NCTId,Condition,Phase,StartDate,EnrollmentCount
&min_rnk=1&max_rnk=1000
&fmt=csv

