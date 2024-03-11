import json
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

from tools.codeplot import PlotGeneratorTool
from components.chat.chathistory import ChatHistory

class Agent:
    def __init__(self , memory: int = 5):
        self.states = ['agent']
        self.memory = memory
        self.chat_history = ChatHistory()
        self.default_values = [None]
        for state, default in zip(self.states, self.default_values):
            if state not in st.session_state:
                st.session_state[state] = default

    @st.cache_resource
    def _initialize_llm(_self) -> ChatOpenAI:
        llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.2 , api_key=st.session_state['api_key'])
        return llm
    
    @st.cache_resource()
    def _create_pandas_agent(_self, df) -> None:

        llm = _self._initialize_llm()

        pandas_agent = create_pandas_dataframe_agent(
            llm, 
            df,
            verbose=True, 
            max_iterations=5, 
            agent_type='openai-tools',
            extra_tools=[PlotGeneratorTool()],
            return_intermediate_steps=True,
            prefix="When asked to generate any plots always use PlotGeneratorTool. They will be automatically rendered. No need to use markdown to render them."
        )
        st.session_state['agent'] = pandas_agent

    def _get_llm_response(self, prompt):
        history = self.chat_history.retrieve_messages(n=self.memory)
        with st.spinner('The assistant is thinking...'):
            response = st.session_state['agent'].invoke(json.dumps(history) + prompt)
            return response