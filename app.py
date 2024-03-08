import os

import streamlit as st
import pandas as pd

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI

from tools.codeplot import PlotGeneratorTool

session_keys = ['api_key',
                'form_submitted', 
                'file_uploaded', 
                'file_processed',
                'df', 
                'file_name', 
                'clicked', 
                'history',
                ]

default_values = ['', 
                  False, 
                  False, 
                  False,
                  None, 
                  '', 
                  False , 
                  {
                    "human":[],
                    "assistant":[]
                  }
                ]

for key, value in zip(session_keys, default_values):
    if key not in st.session_state:
        st.session_state[key] = value

st.title('Data Science Assistant')

def openai_form_submitted():
    st.session_state['form_submitted'] = True
    st.cache_resource.clear()

@st.cache_resource
def initialize_llm():
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=1 , api_key=st.session_state['api_key'])
    return llm

@st.cache_resource()
def create_pandas_agent(_llm, df):

    pandas_agent = create_pandas_dataframe_agent(
        _llm, 
        df, 
        verbose=True, 
        max_iterations=3, 
        agent_type='openai-tools',
        extra_tools=[PlotGeneratorTool()],
        return_intermediate_steps=True,
        prefix="When asked to generate any plots always use PlotGeneratorTool."
    )
    return pandas_agent

def get_llm_response(pandas_agent, prompt):

    with st.spinner('The assistant is thinking...'):
        response = pandas_agent.invoke(prompt)
        return response
    
@st.cache_data()
def load_and_process_file(loaded_file):

    with st.spinner('Loading and processing the file...'):
        import time
        time.sleep(2)  
        df = pd.read_csv(loaded_file, low_memory=False)
        return df

def show_code_expander(code):
    with st.expander("Show code"):
        st.markdown(f'''
                    ```python
                    {code}''', unsafe_allow_html=True)
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

                if not st.session_state['file_processed']:
                    df = load_and_process_file(loaded_file)
                    st.session_state['df'] = df

                st.dataframe(st.session_state['df'])
                st.session_state['file_name'] = loaded_file.name

                llm = initialize_llm()
                pandas_agent = create_pandas_agent(llm, st.session_state['df'])


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
                            if 'plot' in a_message:
                                st.image(a_message['plot'])
                                st.write(a_message['response'])
                            if 'code' in a_message:
                                show_code_expander(a_message['code'])
                            else:
                                st.write(a_message['response'])
    if prompt:
        st.session_state['history']['human'].append(prompt)
        with st.chat_message("human"):
            st.write(prompt)

        try:
            response = get_llm_response(pandas_agent, prompt)
            rendered = False

            current_dir = os.path.dirname(__file__)
            plots_dir = os.path.join(current_dir, 'plots')

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
                            show_code_expander(code)

                    if action.tool == 'python_repl_ast':
                        st.session_state['history']['assistant'].append({"response": response['output'] , "code": action.tool_input['query']})
                        rendered = True
                        with st.chat_message("assistant"):
                            st.write(response['output'])
                            code = action.tool_input['query']
                            show_code_expander(code)
                
            if not rendered:
                st.session_state['history']['assistant'].append({"response": response['output']})
                with st.chat_message("assistant"):
                    st.write(response['output'])

        except Exception as e:
            response = f"An error occurred: {e}"
            st.write(response)


