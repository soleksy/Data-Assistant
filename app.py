import os

import streamlit as st
import pandas as pd

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

from tools.lineplot import LinePlot

session_keys = ['api_key', 'form_submitted', 'file_uploaded', 'file_name', 'clicked', 'history' ]
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

prefix_prompt = "When asked to make a plot always use CreateLinePlot tool. The plot will be automatically generated don't use sandbox to show it."

with st.sidebar:
    st.write('*Welcome to the Data Science Assistant!*')
    st.write('This chatbot is designed to assist you with your data exploratory tasks.')
    st.caption('''
    **Please enter your OpenAI API key.**
    **Then load the CSV file, and start chatting.**
    ''')

    st.divider()

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

                if loaded_file.name not in os.listdir('files'):
                    with open(os.path.join('files', loaded_file.name), "wb") as f:
                        f.write(loaded_file.getbuffer())

                st.session_state['file_uploaded'] = True
                df = pd.read_csv(loaded_file, low_memory=False)
                st.dataframe(df)
                st.session_state['file_name'] = loaded_file.name
                llm = initialize_llm()

                pandas_agent = create_pandas_dataframe_agent(
                    llm, 
                    df, 
                    verbose=True, 
                    max_iterations=3, 
                    agent_type='openai-tools',  
                    extra_tools=[LinePlot()],
                    return_intermediate_steps=True,
                    prefix=prefix_prompt)


if st.session_state['file_uploaded']:
    with st.chat_message("assistant"):
        st.write("Hello!👋 How can I help you today?")
    prompt = st.chat_input("Ask me anything!")

    for h_message, a_message in zip(st.session_state['history']['human'], st.session_state['history']['assistant']):
                if h_message:
                        with st.chat_message("human"):
                            st.write(h_message)
                if a_message:
                    if 'response' in a_message:
                        with st.chat_message("assistant"):
                            st.write(a_message['response'])
                        if 'plot' in a_message:
                            st.image(a_message['plot'])
    if prompt:
        st.session_state['history']['human'].append(prompt)
        with st.chat_message("human"):
            st.write(prompt)

        try:
            response = pandas_agent.invoke(prompt)
            rendered = False
            print(response)
            current_dir = os.path.dirname(__file__)
            plots_dir = os.path.join(current_dir, 'plots')

            if 'intermediate_steps' in response:
                for step in response['intermediate_steps']:
                    action, result = step 
                    if action.tool == 'line_plot':
                        plot_filename = action.tool_input['filename']
                        plot_path = os.path.join(plots_dir, plot_filename)
                        
                        st.session_state['history']['assistant'].append({"response": response['output'] , "plot": plot_path})
                        rendered = True
                        with st.chat_message("assistant"):
                            st.write(response['output'])
                            st.image(plot_path)
            if not rendered:
                st.session_state['history']['assistant'].append({"response": response['output']})
                with st.chat_message("assistant"):
                    st.write(response['output'])

        except Exception as e:
            response = f"An error occurred: {e}"
            st.write(response)