import requests, io
import pandas as pd
import streamlit as st
import altair as alt
from langchain.llms import OpenAI

# Send and retrieve HTTP (REST) request
disease = "parkinson"
min_value = 1
max_value = 5
url = "https://clinicaltrials.gov/api/query/full_studies?expr=" + disease + "&min_rnk=" + str(min_value) + "&max_rnk=" + str(max_value) + "&fmt=csv"
st.text(url)

res = requests.get(url).content

# Extract contents, skip CSV header (first 10 lines), to dataframe
data = pd.read_csv(io.StringIO(res.decode("utf-8")))

st.header("Tableau de données")
st.dataframe(data) 

st.title('🦜🔗 Quickstart App')

openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

def generate_response(input_text):
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    st.info(llm(input_text))

with st.form('my_form'):
    text = st.text_area('Enter text:', 'WHat is the definition of a clinical trial ?')
    submitted = st.form_submit_button('Submit')
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(text)
