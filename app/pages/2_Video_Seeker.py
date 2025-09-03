import streamlit as st
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PATH import METADATA_PATH, FPS_PATH, L28_PATH
from utils import *
from state import init_session_state

st.set_page_config(page_title="Video Seeker", layout='wide')
st.sidebar.header("Video Seeker")

client = load_client()
init_session_state()
load_value("collection_name")
load_value("file_content")

######################
# SUBMISSION SECTION #
######################
st.subheader("Submission")
submission_container = st.container(
    border=True,
    key="submission_container",
)
with submission_container:
    cols = st.columns([0.3, 0.1, 0.6])
    with cols[0]:
        st.text_input(
            label='File name',
            key='file_name',
            width=300,
        )
    with cols[1]:
        st.write("")
        st.write("")
        st.write(".csv")
    st.text_area(
        label="Answer",
        height=150,
        key="_file_content",
        on_change=store_value,
        args=("file_content",)
    )
submission_widget_container = st.container(key='submission_widget_container')
with submission_widget_container:
    cols = st.columns([0.15, 0.15, 0.5])
    with cols[0]:
        st.button("Submit", on_click=submit, icon=":material/assignment:")
    with cols[1]:
        st.button("Clear Submission", on_click=clear_submission, icon=":material/clear_all:")

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
            frame_dir = os.path.join(st.session_state.available_frames_path[st.session_state.collection_name], origin)
            files = [f for f in os.listdir(frame_dir)]
            first_file = min(files)
            frame = os.path.join(frame_dir, first_file)
            if st.session_state.seek_pack == "L28":
                video_data = os.path.join(L28_PATH, origin + ".mp4")
            else:
                metadata = get_video_metadata(METADATA_PATH, origin, ["watch_url"])
                video_data = get_frame_url(FPS_PATH, origin, metadata)
            if st.button(label=origin, key=f"video_{i}", width='content'): 
                show_details(origin=origin,
                             frame_index=0,
                             frame=first_file,
                             data=video_data,
                             frame_path=frame,
                             fps_file=FPS_PATH,
                             video_name=origin)