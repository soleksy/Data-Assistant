import os
import streamlit as st

class Chat:

    def __init__(self , pandas_agent):
        self.pandas_agent = pandas_agent
        self.states = [ 
                     'history',
                    ]
        self.default_values = [
                                {
                                    "human":[],
                                    "assistant":[]
                                }
                            ]
        for state, default in zip(self.states, self.default_values):
            if state not in st.session_state:
                st.session_state[state] = default
    
    def set_state(self, key: str, value: any) -> None:
        st.session_state[key] = value
    
    def get_state(self, key: str) -> any:
        return st.session_state[key]
    
    def get_llm_response(self , prompt):
        with st.spinner('The assistant is thinking...'):
            response = self.pandas_agent.invoke(prompt)
            return response

    def show_code_expander(self, code):
        with st.expander("Show code"):
            st.markdown(f'''
                        ```python
                        {code}''', unsafe_allow_html=True)

    def render(self):
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
                                if 'plot' in a_message:
                                    st.image(a_message['plot'])
                                    st.write(a_message['response'])
                                if 'code' in a_message:
                                    self.show_code_expander(a_message['code'])
                                else:
                                    st.write(a_message['response'])
        if prompt:
            st.session_state['history']['human'].append(prompt)
            with st.chat_message("human"):
                st.write(prompt)

            try:
                response = self.get_llm_response(prompt)
                rendered = False

                root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                plots_dir = os.path.join(root_dir, 'plots')

                if 'intermediate_steps' in response:
                    for step in response['intermediate_steps']:
                        action, result = step 
                        if action.tool == 'plot_generator':
                            
                            plot_filename = str(result)+'.png'
                            plot_path = os.path.join(plots_dir, plot_filename)
                            
                            st.session_state['history']['assistant'].append({"response": response['output'] , "plot": plot_path , "code": action.tool_input['code']})
                            rendered = True
                            with st.chat_message("assistant"):
                                st.image(plot_path)
                                st.write(response['output'])
                                code = action.tool_input['code']
                                self.show_code_expander(code)

                        if action.tool == 'python_repl_ast':
                            st.session_state['history']['assistant'].append({"response": response['output'] , "code": action.tool_input['query']})
                            rendered = True
                            with st.chat_message("assistant"):
                                st.write(response['output'])
                                code = action.tool_input['query']
                                self.show_code_expander(code)
                    
                if not rendered:
                    st.session_state['history']['assistant'].append({"response": response['output']})
                    with st.chat_message("assistant"):
                        st.write(response['output'])

            except Exception as e:
                response = f"An error occurred: {e}"
                st.write(response)