import streamlit as st

from components.sidebar.sidebar import SideBar
from components.chat.chat import Chat
from agent.agent import Agent

st.title('Data Science Assistant')

def main():

    agent = Agent(memory=6)
    
    sidebar = SideBar(agent=agent)
    sidebar.render()

    if sidebar.get_state('file_uploaded'):
        chat = Chat(agent=agent)
        chat.render()

if __name__ == "__main__":
    main()
