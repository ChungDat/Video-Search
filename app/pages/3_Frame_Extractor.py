import streamlit as st
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PATH import KEYFRAMES_PATH, METADATA_PATH, FPS_PATH, L28_PATH
from utils import *
from state import init_session_state
import cv2
from cap_from_youtube import cap_from_youtube

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
            cap = cv2.VideoCapture(video_data)
        else:
            metadata = get_video_metadata(METADATA_PATH, origin, ["author", "channel_url", "publish_date", "title", "watch_url"])
            video_data = get_frame_url(FPS_PATH, origin, metadata)
            cap = cap_from_youtube(video_data)
        VID_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        VID_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        VID_FPS = cap.get(cv2.CAP_PROP_FPS)
        VID_TOTAL_FRAMES = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        start_timestamp_in_s = (start_hour * 3600 + start_minute * 60 + start_second)
        start_timestamp_in_ms = start_timestamp_in_s * 1000
        end_timestamp_in_s = (end_hour * 3600 + end_minute * 60 + end_second)
        end_timestamp_in_ms = end_timestamp_in_s * 1000
        start_frame = start_timestamp_in_s * VID_FPS
        st.session_state.start_frame = start_frame
        end_frame = end_timestamp_in_s * VID_FPS
        current_frame = start_frame

        if end_timestamp_in_s != 0 and end_timestamp_in_s < start_timestamp_in_s: # End timestamp is smaller than start timestamp
            st.warning("Invalid end timestamp")
        elif start_frame >= VID_TOTAL_FRAMES:
            st.warning("Invalid start timestamp")
        else:
            if end_timestamp_in_s == 0: # End timestamp is empty
                end_timestamp_in_s = start_timestamp_in_s + 3 * 60 # Extract frame for 3 minutes long
                end_timestamp_in_ms = end_timestamp_in_s * 1000
                end_frame = end_timestamp_in_s * VID_FPS
                
            # End timestamp is bigger than start timestamp
            cap.set(cv2.CAP_PROP_POS_MSEC, start_timestamp_in_ms)

            st.session_state.frames = []
            count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.resize(frame, dsize=None, fx=1/3, fy=1/3, interpolation=cv2.INTER_LINEAR)
                if (count % st.session_state.step == 0):
                    st.session_state.frames.append(frame)
                current_frame += 1
                if current_frame == end_frame:
                    break
                count += 1
            cap.release()
for i, frame in enumerate(st.session_state.frames):
    with cols[i % 10]:
        st.image(frame, f"{st.session_state.start_frame + i * st.session_state.step + 1}", channels="BGR")
