import streamlit as st
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PATH import KEYFRAMES_PATH, METADATA_PATH, MAP_KEYFRAMES_PATH
from utils import *
from state import init_session_state

st.set_page_config(page_title="Query Engine", layout='wide')
st.sidebar.header("Query Engine")

COLLECTION_NAME = "my_collection"
model = load_model()
client = load_client()
init_session_state()

st.selectbox(
    label="Select Query Mode",
    options=["Text Query", "Image Query"],
    key="query_mode",
    width=150,
)

if st.session_state.query_mode == "Text Query":
    st.subheader("Text Query")
    input_container = st.container(height=150, border=True, key='query_scroll')
    with input_container:
        for i, inp in enumerate(st.session_state.inputs):
            cols = st.columns([0.6, 0.2, 0.1])
            with cols[0]:
                st.session_state.inputs[i]["query"] = st.text_area(
                    f"Query",
                    key=f"query_{inp['id']}",
                    height=100,
                    on_change=update_input_query,
                    args=(i,),
                )
            with cols[1]:
                st.session_state.inputs[i]["tags"] = st.multiselect(
                    label="Tag",
                    options=st.session_state.tags,
                    key=f"tag_{inp['id']}",
                    on_change=update_input_tags,
                    args=(i,),
                )
            with cols[2]:
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

query_widget_container = st.container(height='content', key='query_widget')
with query_widget_container:
    cols = st.columns([0.15, 0.15, 0.15, 0.3])
    with cols[0]:
        st.button("🔍 Search", on_click=search_query, args=(st.session_state.query_mode, model, client, COLLECTION_NAME))
    with cols[1]:
        st.button("➕ Add Input", on_click=add_input)
    with cols[2]:
        st.button("Clear Inputs", on_click=clear_input, icon=":material/clear_all:")
    with cols[3]:
        st.button("Check Server", on_click=check_server, args=(client, COLLECTION_NAME), icon=":material/database:")

# ######################
# # SUBMISSION SECTION #
# ######################
st.subheader("Submission")
submission_container = st.container(
    border=True,
    key="submission_scroll",
    height="content",
)
with submission_container:
    st.text_input(
        label='File name',
        key='file_name',
        width=300,
    )
    st.text_area(
        label="Answer",
        height=150,
        key="file_content",
    )
submission_widget_container = st.container(height='content', key='submission_widget')
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
result_widget_container = st.container(height='content', border=True, key='result_widget')
with result_widget_container:
    cols = st.columns([4, 1])
    with cols[0]:
        num_of_cols = st.slider("Number of columns", min_value=10, max_value=20, value=10, step=1)
    with cols[1]:
        st.toggle("Sort by video", key="sort_by_video")

result_container = st.container(height=300, border=False, key='result_scroll')
with result_container:
    if not st.session_state.sort_by_video:
        cols = st.columns(num_of_cols)
        for i, hit in enumerate(st.session_state.results):
            origin = hit.payload.get("origin")
            keyframe_id = hit.payload.get("keyframe_id")
            metadata = get_video_metadata(METADATA_PATH, origin, ["author", "channel_url", "publish_date", "title", "watch_url"])
            start_time = get_keyframe_start_time(MAP_KEYFRAMES_PATH, origin, keyframe_id)
            url = get_keyframe_url(MAP_KEYFRAMES_PATH, origin, metadata)
            if keyframe_id < 10:
                keyframe_id = f"00{keyframe_id}"
            elif keyframe_id < 100:
                keyframe_id = f"0{keyframe_id}"
            else:
                keyframe_id = str(keyframe_id)
            # frame = hit.payload.get("frame")
            image_path = os.path.join(KEYFRAMES_PATH, origin, keyframe_id + ".jpg")

            with cols[i % num_of_cols]:
                st.image(image_path)
                if st.button("Details", key=f"image_{i}", width='stretch'):
                    show_image_details(
                        info=f"From video: {origin}\nKeyframe ID: {keyframe_id}",
                        video=url,
                        image=image_path,
                        start_time=start_time
                    )

    else:
        for video in st.session_state.video_list:
            video_hits = []
            for hit in st.session_state.results_sorted:
                if not video_hits and hit.payload.get("origin") == video:
                    video_hits.append(hit)
                elif video_hits:
                    if hit.payload.get("origin") == video:
                        video_hits.append(hit)
                    else:
                        break
            st.markdown(f"### {video}")
            cols = st.columns(num_of_cols)
            for i, hit in enumerate(video_hits):
                origin = hit.payload.get("origin")
                if origin != video:
                    continue
                keyframe_id = hit.payload.get("keyframe_id")
                metadata = get_video_metadata(METADATA_PATH, origin, ["author", "channel_url", "publish_date", "title", "watch_url"])
                start_time = get_keyframe_start_time(MAP_KEYFRAMES_PATH, origin, keyframe_id)
                url = get_keyframe_url(MAP_KEYFRAMES_PATH, origin, metadata)
                if keyframe_id < 10:
                    keyframe_id = f"00{keyframe_id}"
                elif keyframe_id < 100:
                    keyframe_id = f"0{keyframe_id}"
                else:
                    keyframe_id = str(keyframe_id)
                # frame = hit.payload.get("frame")
                image_path = os.path.join(KEYFRAMES_PATH, origin, keyframe_id + ".jpg")

                with cols[i % num_of_cols]:
                    st.image(image_path)
                    if st.button("Details", key=f"image_{video}_{i}", width='stretch'):
                        show_image_details(
                            info=f"From video: {origin}\nKeyframe ID: {keyframe_id}",
                            video=url,
                            image=image_path,
                            start_time=start_time
                        )
            st.write("---")