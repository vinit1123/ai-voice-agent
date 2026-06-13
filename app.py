import streamlit as st

from agent_backend import (
    ask_agent
)

st.set_page_config(
    page_title="AI Voice Agent",
    page_icon="🤖"
)

st.title(
    "🤖 AI Voice Agent"
)

question = st.text_input(
    "Ask Something"
)

if st.button("Send"):

    answer = ask_agent(
        question
    )

    st.write(
        f"🤖 {answer}"
    )