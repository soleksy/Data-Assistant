import os
import uuid
import streamlit as st

from components.chat.chathistory import ChatHistory
from agent.agent import Agent

class Chat:
    def __init__(self,  agent: Agent):
        self.agent = agent
        self.chat_history = self._initialize_chat_history()
        
    @st.cache_resource()
    def _initialize_chat_history(_self) -> ChatHistory:
        return ChatHistory()
    
    def _render_last_prompt(self, prompt: str) -> None:
        with st.chat_message("human"):
            st.write(prompt)

    def render(self) -> None:

        with st.chat_message("assistant"):
            st.write("Hello!👋 How can I help you today?")

        prompt = st.chat_input("Ask me anything!")
        self.chat_history.render_history()

        if prompt:
            self._render_last_prompt(prompt)
            self.chat_history.add_message_human(prompt)
            
            response = self.agent._get_llm_response(prompt)

            root_dir = os.path.dirname(os.path.dirname(os.path.dirname((__file__))))
            plots_dir = os.path.join(root_dir, 'plots')

            intermediate_steps = []
            if 'intermediate_steps' in response:
                for step in response['intermediate_steps']:
                    action, result = step
                    if action.tool == 'plot_generator':
                        plot_filename = str(result)+'.png' if type(result)==uuid.UUID else None
                        if plot_filename:
                            plot_path = os.path.join(plots_dir, plot_filename)
                            intermediate_steps.append({'response': response['output'], 'plot_path': plot_path, 'code': action.tool_input['code']})

                    if action.tool == 'python_repl_ast':
                        intermediate_steps.append({'response': response['output'], 'plot_path': None, 'code': action.tool_input['query']})
            
            else:
                self.chat_history.add_message_assistant(response=[{'response': response['output']}])

            self.chat_history.add_message_assistant(response=intermediate_steps)
            self.chat_history.render_last_assistant_message()
            

