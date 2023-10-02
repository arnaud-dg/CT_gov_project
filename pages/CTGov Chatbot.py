import openai
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

openai.api_key = st.secrets["OPENAI_API_KEY"]

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "What is Streamlit?"}
  ]
)

st.write(completion.choices[0].message.content)

# import openai
# import re
# import streamlit as st
# from prompts import get_system_prompt

# st.title("☃️ Frosty")

# # Initialize the chat messages history
# openai.api_key = st.secrets["OPENAI_API_KEY"]
# if "messages" not in st.session_state:
#     # system prompt includes table information, rules, and prompts the LLM to produce
#     # a welcome message to the user.
#     st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]

# # Prompt for user input and save
# if prompt := st.chat_input():
#     st.session_state.messages.append({"role": "user", "content": prompt})

# # display the existing chat messages
# for message in st.session_state.messages:
#     if message["role"] == "system":
#         continue
#     with st.chat_message(message["role"]):
#         st.write(message["content"])
#         if "results" in message:
#             st.dataframe(message["results"])

# # If last message is not from assistant, we need to generate a new response
# if st.session_state.messages[-1]["role"] != "assistant":
#     with st.chat_message("assistant"):
#         response = ""
#         resp_container = st.empty()
#         for delta in openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
#             stream=True,
#         ):
#             response += delta.choices[0].delta.get("content", "")
#             resp_container.markdown(response)

#         message = {"role": "assistant", "content": response}
#         # Parse the response for a SQL query and execute if available
#         sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
#         if sql_match:
#             sql = sql_match.group(1)
#             conn = st.experimental_connection("snowpark")
#             message["results"] = conn.query(sql)
#             st.dataframe(message["results"])
#         st.session_state.messages.append(message) 
