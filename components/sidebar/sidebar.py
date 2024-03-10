import os
import streamlit as st
import pandas as pd

from langchain.agents import AgentExecutor
from agent.agent import Agent

class SideBar:

    def __init__(self , agent: Agent):
        self.agent = agent
        self.states = [
                    'api_key',
                    'form_submitted', 
                    'file_uploaded', 
                    'file_processed',
                    'df', 
                    'file_name', 
                    'clicked',
                    'agent'
                    ]
        self.default_values = [
                                '', 
                                False, 
                                False, 
                                False,
                                None, 
                                '', 
                                False,
                                None
                    ]
        for state, default in zip(self.states, self.default_values):
            if state not in st.session_state:
                st.session_state[state] = default
        
    def set_state(self, key: str, value: any) -> None:
        st.session_state[key] = value
    
    def get_state(self, key: str) -> any:
        return st.session_state[key]

    def _openai_form_submitted(self) -> None:
        st.session_state['form_submitted'] = True
        st.cache_resource.clear()

    @st.cache_data()
    def _load_and_process_file(_self, _loaded_file) -> pd.DataFrame:

        with st.spinner('Loading and processing the file...'):
            import time
            time.sleep(2)  
            df = pd.read_csv(_loaded_file, low_memory=False)
            return df
    


    def render(self) -> AgentExecutor:
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

                st.text_input("API Key", key="api_key")
                st.form_submit_button("Submit", on_click=self._openai_form_submitted)
            
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

                        if not st.session_state['file_processed']:
                            df = self._load_and_process_file(loaded_file)
                            st.session_state['df'] = df

                        st.dataframe(st.session_state['df'])
                        st.session_state['file_name'] = loaded_file.name

  
                        return self.agent._create_pandas_agent(df=st.session_state['df'])