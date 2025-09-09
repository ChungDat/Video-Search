import streamlit as st
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PATH import METADATA_PATH, FPS_PATH, L28_PATH, KEYFRAMES_PATH
from utils import *
from state import init_session_state

st.set_page_config(page_title="Video Seeker", layout='wide')
st.sidebar.header("Video Seeker")
st.empty()
client = load_client()
init_session_state()
load_value("collection_name")
load_value("file_content")
disable_scroll_bar()

# Custom CSS for a more compact and polished sidebar
st.markdown('''
<style>
    /* General sidebar enhancements */
    [data-testid="stSidebar"] {
        width: 350px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="stSidebar"] .stButton button {
        margin-top: 0.5em;
    }
    [data-testid="stSidebar"] .stExpander {
        border: none;
    }
    [data-testid="stSidebar"] .stExpander summary {
        padding: 0.5rem 0;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.8rem;
        padding-top: 0;
        margin-top: 0;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-size: 1.4rem;
    }
    [data-testid="stSidebar"] .stTabs [data-testid="stMarkdownContainer"] {
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] .stTextArea textarea {
        height: 80px !important;
    }
</style>
''', unsafe_allow_html=True)

with st.sidebar:
    # --- Submission Section ---
    st.header("Submission")
    
    cols = st.columns([3, 1])
    cols[0].text_input('File name', key='file_name', placeholder="e.g., results_01")
    cols[1].write("`.csv`")
    
    st.text_area(
        "Answers",
        key="_file_content",
        on_change=store_value,
        args=("file_content",),
        placeholder="Add answers for your submission file here...",
        height=100
    )
    
    cols = st.columns(2)
    cols[0].button("Submit", key="submit_button", on_click=submit, icon=":material/assignment:", use_container_width=True)
    cols[1].button("Clear", key="clear_submission_button", on_click=clear_submission, icon=":material/clear_all:", use_container_width=True)

with st.container():
    origin_container = st.container(key="origin_container")
    with origin_container:
        cols = st.columns([0.2, 0.3, 0.5])
        with cols[0]:
            st.selectbox(
                label="Pack",
                options=st.session_state.available_packs,
                key="seek_pack",
                index=None,
                )
        with cols[1]:
            seek_videos = st.session_state.available_videos_per_pack.get(st.session_state.seek_pack, [])
            st.multiselect(
                label="Videos",
                options=seek_videos,
                key="seek_videos",
            )

        if st.session_state.seek_pack:
            cols = st.columns(10)
            if st.session_state.seek_videos:
                origins = [st.session_state.seek_pack + '_' + video for video in st.session_state.seek_videos]
            else:
                origins = [st.session_state.seek_pack + '_' + video for video in st.session_state.available_videos_per_pack[st.session_state.seek_pack]]

        for i, origin in enumerate(origins):
            with cols[i % 10]:
                frame = os.path.join(KEYFRAMES_PATH, origin, "001.jpg")
                if st.session_state.seek_pack == "L28":
                    video_data = os.path.join(L28_PATH, origin + ".mp4")
                else:
                    metadata = get_video_metadata(METADATA_PATH, origin, ["watch_url"])
                    video_data = get_frame_url(FPS_PATH, origin, metadata)
                if st.button(label=origin, key=f"video_{i}", width='content'): 
                    show_details(origin=origin,
                                frame_index=0,
                                frame="001.jpg",
                                data=video_data,
                                frame_path=frame,
                                fps_file=FPS_PATH,
                                video_name=origin)