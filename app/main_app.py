import streamlit as st
from state import init_session_state
from utils import disable_scroll_bar

st.set_page_config(
    page_title="main app",
    page_icon="👋",
)
init_session_state()
disable_scroll_bar()

st.switch_page("pages/1_Query_Engine.py")