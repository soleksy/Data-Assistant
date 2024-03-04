import streamlit as st
import pandas as pd

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
# Initialize session state variables more concisely
session_keys = ['api_key', 'form_submitted', 'file_uploaded', 'file_name', 'clicked', 'history']
default_values = ['', False, False, '', False , {
    "human":[],
    "assistant":[]
}]
for key, value in zip(session_keys, default_values):
    if key not in st.session_state:
        st.session_state[key] = value

st.title('Data Science Assistant')


def openai_form_submitted():
    st.session_state['form_submitted'] = True

def initialize_llm():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0 , api_key=st.session_state['api_key'])
    return llm


with st.sidebar:
    st.write('*Welcome to the Data Science Assistant!*')
    st.write('This chatbot is designed to assist you with your data exploratory tasks.')
    st.caption('''
    **Please enter your OpenAI API key.**
    **Then load the CSV file, and start chatting.**
    ''')

    st.divider()

    # Form for OpenAI API Key
    with st.form("openai_api_key_form"):

        if st.session_state['form_submitted']:
            st.write(f"Currently loaded key: {st.session_state['api_key']}")
        else:
            st.write("Please enter your OpenAI API key to get started.")

        new_api_key = st.text_input("API Key", key="api_key")
        submitted_api_key = st.form_submit_button("Submit", on_click=openai_form_submitted)
    
    if st.session_state['form_submitted']:
        st.divider()
        if st.button("Load CSV File" , type='primary'):
            st.session_state['clicked'] = True
        if st.session_state['clicked']:
            loaded_file = st.file_uploader("Choose a file", type=["csv"], key="file_uploader")
            if loaded_file is not None:
                st.session_state['file_uploaded'] = True
                df = pd.read_csv(loaded_file, low_memory=False)
                st.dataframe(df)
                st.session_state['file_name'] = loaded_file.name
                llm = initialize_llm()
                pandas_agent = create_pandas_dataframe_agent(llm, df, verbose=True, max_iterations=3)

if st.session_state['file_uploaded']:
    with st.chat_message("assistant"):
        st.write("Hello!👋 How can I help you today?")
    prompt = st.chat_input("Ask me anything!")
    if prompt:

        for h_message, a_message in zip(st.session_state['history']['human'], st.session_state['history']['assistant']):
                if h_message:
                        with st.chat_message("human"):
                            st.write(h_message)
                if a_message:
                        with st.chat_message("assistant"):
                            st.write(a_message)
                            
        st.session_state['history']['human'].append(prompt)
        with st.chat_message("human"):
            st.write(prompt)

        try:
            response = pandas_agent(prompt)
            st.session_state['history']['assistant'].append(response['output'])
            with st.chat_message("assistant"):
                st.write(response['output'])

        except Exception as e:
            response = f"An error occurred: {e}"
            st.write(response)