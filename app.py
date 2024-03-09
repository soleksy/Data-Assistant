import streamlit as st

from components.sidebar.sidebar import SideBar
from components.chat.chat import Chat

st.title('Data Science Assistant')

def main():

    sidebar = SideBar()
    pandas_agent = sidebar.render()

    if sidebar.get_state('file_uploaded'):
        chat = Chat(pandas_agent)
        chat.render()

if __name__ == "__main__":
    main()
