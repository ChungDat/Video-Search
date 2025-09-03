import streamlit as st
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PATH import METADATA_PATH, FPS_PATH, L28_PATH
from utils import *
from state import init_session_state

st.set_page_config(page_title="Query Engine", layout='wide')
st.sidebar.header("Query Engine")

model = load_model()
client = load_client()
init_session_state()
load_value("collection_name")
load_value("file_content")

collection_container = st.container(key="collection_container",)
with collection_container:
    cols = st.columns([0.2, 0.15, 0.5])
    with cols[0]:
        st.selectbox(
            label="Select Database Collection",
            options=st.session_state.collections,
            key="_collection_name",
            on_change=store_value,
            args=("collection_name",),
        )

    with cols[1]:
        st.write("")
        st.button("Check Server", on_click=check_server, args=(client, st.session_state.collection_name), icon=":material/database:")

st.selectbox(
    label="Select Query Mode",
    options=["Text Query", "Image Query"],
    key="query_mode",
    width=150,
)

st.button("Save log", key="log_button", on_click=save_log)

if st.session_state.query_mode == "Text Query":
    st.subheader("Text Query")
    input_container = st.container(height=150, border=True, key='input_container')
    with input_container:
        for i, inp in enumerate(st.session_state.inputs):
            cols = st.columns([0.6, 0.1])
            with cols[0]:
                st.session_state.inputs[i]["query"] = st.text_area(
                    f"Query",
                    key=f"query_{inp['id']}",
                    height=100,
                    on_change=update_input_query,
                    args=(i,),
                )
            with cols[1]:
                if len(st.session_state.inputs) > 1:
                    st.button(
                        label="🗑️", 
                        key=f"remove_input_{inp['id']}", 
                        on_click=remove_input, 
                        args=(inp["id"],),
                    )

elif st.session_state.query_mode == "Image Query":
    st.subheader("Image Similarity Search")
    st.file_uploader(
        label="Upload an image",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=False,
        key="image_upload",
    )

query_widget_container = st.container(height='content', key='query_widget_container')
with query_widget_container:
    cols = st.columns([0.15, 0.15, 0.5])
    with cols[0]:
        st.button("➕ Add Input", on_click=add_input)
    with cols[1]:
        st.button("Clear Inputs", on_click=clear_input, icon=":material/clear_all:")

##################
# FILTER SECTION #
##################
st.subheader("Filter")
filter_container = st.container(key="filter_container", border=True)
with filter_container:
    cols = st.columns([0.2, 0.2, 0.15, 0.3])
    with cols[0]:
        st.multiselect("Packs", options=st.session_state.available_packs, key="filter_packs")
    with cols[1]:
        filter_tags = []
        for pack in st.session_state.filter_packs:
            filter_tags.extend(st.session_state.available_tags.get(pack, []))
        st.multiselect("Tags", options=filter_tags, key="filter_tags")
    with cols[2]:
        st.write("L21, tin tức, 60 giây sáng  \nL22, tin tức, 60 giây chiều  \nL23, thể thao, đua xe đạp  \nL24, thể thao, lân sư rồng  \nL25, học tập, ôn thi thpt")
    with cols[3]:
        st.write("L26, ẩm thực, món ngon mỗi ngày  \nL27, du lịch văn hoá, VN đi là ghiền  \nL28, du lịch văn hoá, tản mạn Mê Kông  \nL29, du lịch văn hoá, đôi mắt Mê Kông  \nL30, đời sống, lan toả năng lượng tích cực")


st.button("🔍 Search", on_click=search_query, args=(st.session_state.query_mode, model, client, st.session_state.collection_name, 300))

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

##################
# RESULT SECTION #
##################
st.subheader("Search Results")
result_widget_container = st.container(border=True, key='result_widget_container')
with result_widget_container:
    cols = st.columns([4, 1])
    with cols[0]:
        num_of_cols = st.slider("Number of columns", min_value=10, max_value=20, value=10, step=1)
    with cols[1]:
        st.toggle("Sort by video", key="sort_by_video")

result_container = st.container(height=500, border=False, key='result_container')
with result_container:
    if not st.session_state.sort_by_video:
        cols = st.columns(num_of_cols)
        for i, hit in enumerate(st.session_state.results):
            pack = hit.payload.get("pack")
            video = hit.payload.get("video")
            frame_index = hit.payload.get("frame_index")
            frame = hit.payload.get("frame")
            origin = pack + '_' + video
            metadata = get_video_metadata(METADATA_PATH, origin, ["watch_url"])
            start_time = get_frame_start_time(FPS_PATH, origin, frame_index)
            if frame_index < 10:
                frame_index = f"00{frame_index}"
            elif frame_index < 100:
                frame_index = f"0{frame_index}"
            else:
                frame_index = str(frame_index)
            frame_path = os.path.join(st.session_state.available_frames_path[st.session_state.collection_name], origin, frame)
            if pack == "L28":
                video_data = os.path.join(L28_PATH, origin + ".mp4")
            else:
                video_data = get_frame_url(FPS_PATH, origin, metadata)

            with cols[i % num_of_cols]:
                st.image(frame_path)
                if st.button("Details", key=f"image_{i}", width='stretch'):
                    show_details(
                        origin=origin,
                        frame_index=frame_index,
                        frame=frame,
                        data=video_data,
                        frame_path=frame_path,
                        start_time=start_time,
                        fps_file=FPS_PATH,
                        video_name=origin,
                    )
    else:
        for i, candidate in enumerate(st.session_state.origin_rank):
            video_hits = []
            for hit in st.session_state.results_sorted:
                pack = hit.payload.get("pack")
                video = hit.payload.get("video")
                origin = pack + '_' + video
                if not video_hits and origin == candidate:
                    video_hits.append(hit)
                elif video_hits:
                    if origin == candidate:
                        video_hits.append(hit)
                    else:
                        break
            st.markdown(f"### {i + 1}. {candidate}")
            cols = st.columns(num_of_cols)
            for i, hit in enumerate(video_hits):
                pack = hit.payload.get("pack")
                video = hit.payload.get("video")
                frame = hit.payload.get("frame")
                frame_index = hit.payload.get("frame_index")
                origin = pack + '_' + video
                metadata = get_video_metadata(METADATA_PATH, origin, ["watch_url"])
                start_time = get_frame_start_time(FPS_PATH, origin, frame_index)
                if frame_index < 10:
                    frame_index = f"00{frame_index}"
                elif frame_index < 100:
                    frame_index = f"0{frame_index}"
                else:
                    frame_index = str(frame_index)
                frame_path = os.path.join(st.session_state.available_frames_path[st.session_state.collection_name], origin, frame)
                if hit.payload.get("pack") == "L28":
                    video_data = os.path.join(L28_PATH, origin + ".mp4")
                else:
                    video_data = get_frame_url(FPS_PATH, origin, metadata)

                with cols[i % num_of_cols]:
                    st.image(frame_path)
                    if st.button("Details", key=f"image_{candidate}_{i}", width='stretch'):
                        show_details(
                            origin=origin,
                            frame_index=frame_index,
                            frame=frame,
                            data=video_data,
                            frame_path=frame_path,
                            start_time=start_time,
                            fps_file=FPS_PATH,
                            video_name=origin,
                        )
            st.write("---")