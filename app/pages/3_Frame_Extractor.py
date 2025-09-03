import streamlit as st
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PATH import METADATA_PATH, FPS_PATH, L28_PATH
from utils import *
from state import init_session_state
import time

st.set_page_config(page_title="Frame Extrator", layout='wide')
st.sidebar.header("Frame Extractor")

init_session_state()


st.subheader("Select Video")
origin_container = st.container(key="origin_container")
with origin_container:
    cols = st.columns([0.2, 0.2, 0.6])
    with cols[0]:
        st.selectbox(
            label="Pack",
            options=st.session_state.available_packs,
            key="extract_pack",
            index=None,
        )
    with cols[1]:
        extract_video = st.session_state.available_videos_per_pack.get(st.session_state.extract_pack, [])
        st.selectbox(
            label="Videos",
            options=extract_video,
            key="extract_video",
        )

st.subheader("Timestamp")
timestamp_container = st.container(key="timestamp_container")
with timestamp_container:
    cols = st.columns(3)
    with cols[0]:
        st.write("Start timestamp")
        start_cols = st.columns([0.2, 0.2, 0.2, 0.4])
        with start_cols[0]:
            start_hour = st.number_input(label="Hour", min_value=0, key="start_hour")
        with start_cols[1]:
            start_minute = st.number_input(label="Minute", min_value=0, key="start_minute")
        with start_cols[2]:
            start_second = st.number_input(label="Second", min_value=0, key="start_second")
    with cols[1]:
        st.write("End timestamp")
        start_cols = st.columns([0.2, 0.2, 0.2, 0.4])
        with start_cols[0]:
            end_hour = st.number_input(label="Hour", min_value=0, key="end_hour")
        with start_cols[1]:
            end_minute = st.number_input(label="Minute", min_value=0, key="end_minute")
        with start_cols[2]:
            end_second = st.number_input(label="Second", min_value=0, key="end_second")
    with cols[2]:
        st.slider(label="Step", key="step", min_value=5, max_value=30, step=5)

cols = st.columns(10)
if st.button("Extract Frame", key="extract_frame"):
    if not st.session_state.extract_pack:
        st.warning("Please select a pack")
    if not st.session_state.extract_video:
        st.warning("Please select a video")
    else:
        origin = st.session_state.extract_pack + '_' + st.session_state.extract_video
        if st.session_state.extract_pack == "L28":
            video_data = os.path.join(L28_PATH, origin + ".mp4")
            fromYoutube = False
        else:
            metadata = get_video_metadata(METADATA_PATH, origin, ["length", "watch_url"])
            video_data = get_frame_url(FPS_PATH, origin, metadata)
            fromYoutube = True

        start_timestamp_in_s = (start_hour * 3600 + start_minute * 60 + start_second)
        end_timestamp_in_s = (end_hour * 3600 + end_minute * 60 + end_second)

        if end_timestamp_in_s != 0 and end_timestamp_in_s < start_timestamp_in_s: # End timestamp is smaller than start timestamp
            st.warning("Invalid end timestamp")
        # elif start_timestamp_in_s >= metadata["length"]:
        #     st.warning("Invalid start timestamp")
        else:
            if end_timestamp_in_s == 0: # End timestamp is empty
                end_timestamp_in_s = start_timestamp_in_s + 1 * 60 + 30 # Extract frame for 1.5 minutes long

            start_time = time.time()
            st.session_state.frames, st.session_state.fps = sample_frames_2(video_data, fromYoutube, start_timestamp_in_s, end_timestamp_in_s, st.session_state.step, 0.5)
            end_time = time.time()
            st.session_state.start_frame = start_timestamp_in_s * st.session_state.fps
            st.write(f"Process time : {end_time - start_time}")
for i, frame in enumerate(st.session_state.frames):
    with cols[i % 10]:
        st.image(frame, f"{st.session_state.start_frame + i * st.session_state.step + 1}", channels="BGR")
