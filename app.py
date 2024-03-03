import streamlit as st
import pandas as pd

# Initialize session state variables more concisely
session_keys = ['api_key', 'form_submitted', 'file_uploaded', 'file_name', 'clicked']
default_values = ['', False, False, '', False]
for key, value in zip(session_keys, default_values):
    if key not in st.session_state:
        st.session_state[key] = value

st.title('Data Science Assistant')

def openai_form_submitted():
    st.session_state['form_submitted'] = True

def change_state():
    st.session_state['clicked'] = True

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
        if st.button("Load CSV File"):
            st.session_state['clicked'] = True
        if st.session_state['clicked']:
            loaded_file = st.file_uploader("Choose a file", type=["csv"], key="file_uploader")
            if loaded_file is not None:
                st.session_state['file_uploaded'] = True
                df = pd.read_csv(loaded_file, low_memory=False)

                st.dataframe(df)
