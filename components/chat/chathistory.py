import streamlit as st

from pydantic import BaseModel
from typing import Optional , List , Union

class HumanChatMessage(BaseModel):
    message: str

class AssistantChatMessage(BaseModel):
    response: str
    plot_path: Optional[str] = None 
    code: Optional[str] = None

class ChatHistory:
    def __init__(self):
        if 'history' not in st.session_state:
            st.session_state['history'] = []

    def add_message_human(self, message: str) -> None:

        st.session_state['history'].append(HumanChatMessage(message=message))

    def add_message_assistant(self, response: List[dict]) -> None:

        validate_response =[AssistantChatMessage(**step) for step in response]
        st.session_state['history'].append(validate_response)

    def get_history(self) -> List[Union[HumanChatMessage, List[AssistantChatMessage]]]:

        return st.session_state['history']

    def get_last_assistant_message(self) -> List[AssistantChatMessage]:

        history = self.get_history()
        return history[-1] if history else None

    def clear_history(self) -> None:

        st.session_state['history'] = []

    def render_last_assistant_message(self) -> None:

        history = self.get_history()
        if history:
            last_message = self.get_last_assistant_message()
            response_rendered = False

            with st.chat_message("assistant"):
                for step in last_message:
                    if not response_rendered:
                        st.write(step.response)
                        response_rendered = True
                    if step.plot_path:
                        st.image(step.plot_path)
                    if step.code:
                        self.show_code_expander(step.code)

    def render_history(self) -> None:

        for message in self.get_history():
            if isinstance(message, HumanChatMessage):
                with st.chat_message("human"):
                    st.write(message.message)
            else:
                response_rendered = False
                with st.chat_message("assistant"):
                    for step in message:
                        if not response_rendered:
                            st.write(step.response)
                            response_rendered = True
                            
                        if step.plot_path:
                            st.image(step.plot_path)
                        if step.code:
                            self.show_code_expander(step.code)

    def show_code_expander(self, code) -> None:

        with st.expander("Show code"):
            st.code(code)
