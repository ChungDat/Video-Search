import streamlit as st
from state import init_session_state

st.set_page_config(
    page_title="main app",
    page_icon="👋",
)
init_session_state()
st.switch_page("pages/1_Query_Engine.py")