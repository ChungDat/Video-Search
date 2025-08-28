import streamlit as st
import os
from PATH import KEYFRAMES_PATH, METADATA_PATH, MAP_KEYFRAMES_PATH
from utils import get_video_metadata, get_keyframe_url, get_keyframe_start_time
from strlit_utils import *
from strlit_state import init_session_state

COLLECTION_NAME = "my_collection"
model = load_model()
client = load_client()

st.set_page_config(page_title="Visual Browser Search", layout="wide")
st.sidebar.title("Options")
init_session_state()

st.selectbox(
    label="Select Query Mode",
    options=["Text Query", "Image Query"],
    index=0,
    key="query_mode",
    width=200,
)

if st.session_state.query_mode == "Text Query":
    st.subheader("Text Query")
    input_container = st.container(height=150, border=True, key='queries_scroll')
    with input_container:
        for i, inp in enumerate(st.session_state.inputs):
            cols = st.columns([0.6, 0.2, 0.1])
            with cols[0]:
                st.session_state.inputs[i]["query"] = st.text_area(
                    f"Query",
                    key=f"query_{inp['id']}",
                    height=100,
                    on_change=update_input,
                    args=(i,),
                )
            with cols[1]:
                st.session_state.inputs[i]["tags"] = st.multiselect(
                    label="Tag",
                    options=st.session_state.tags,
                    key=f"tag_{inp['id']}",
                    on_change=update_tags,
                    args=(i,),
                )
            with cols[2]:
                if len(st.session_state.inputs) > 1:
                    st.button(
                        label="🗑️", 
                        key=f"remove_{inp['id']}", 
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

button_container = st.container(height='content', key='buttons')
with button_container:
    cols = st.columns([0.15, 0.15, 0.15, 1 - 0.45])
    with cols[0]:
        st.button("🔍 Search", on_click=search_query, args=(st.session_state.query_mode, model, client, COLLECTION_NAME))
    with cols[1]:
        st.button("➕Add Input", on_click=add_input)
    with cols[2]:
        st.button("Check Server", on_click=check_server, args=(client, COLLECTION_NAME), icon=":material/database:")

st.subheader("Search Results") # Dummy results for demonstration
result_widget_container = st.container(height='content', border=True, key='result_widget')
with result_widget_container:
    cols = st.columns([4, 1])
    with cols[0]:
        num_of_cols = st.slider("Number of columns", min_value=10, max_value=20, value=10, step=1)
    with cols[1]:
        st.toggle("Sort by video", key="sort_by_video")

result_container = st.container(height=430, border=False, key='results_scroll')
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