import streamlit as st
import os
from PATH import KEYFRAMES_PATH, METADATA_PATH, MAP_KEYFRAMES_PATH
from utils import get_video_metadata, get_keyframe_url, get_keyframe_start_time

def add_input():
    st.session_state.next_input_id += 1
    st.session_state.inputs.append({
        "id": st.session_state.next_input_id,
        "query": "",
        "tags": [],
    })

def remove_input(id):
    if len(st.session_state.inputs) > 1:
        st.session_state.inputs = [inp for inp in st.session_state.inputs if inp["id"] != id]

def update_input(i):
    st.session_state.inputs[i]["query"] = st.session_state[f"query_{st.session_state.inputs[i]['id']}"]

def update_tags(i):
    st.session_state.inputs[i]["tags"] = st.session_state[f"tag_{st.session_state.inputs[i]['id']}"]

@st.cache_data
def create_filters(tags):
    from qdrant_client.http import models
    if not tags:
        return None
    return models.Filter(
        must=[
            models.FieldCondition(
                key="tags",
                match=models.MatchValue(value=tag)
            )
            for tag in tags
        ]
    )

def search_query(mode: str):
    """Perform search based on the current inputs and update results in session state.
    
    Args:
        mode (str): The mode of the query, either "Text Query" or "Image Query".
    Returns:
        None
    """
    if mode == 'Text Query':
        queries = []
        tags = []
        for inp in st.session_state.inputs:
            if inp["query"]:
                queries.append(inp["query"])
            if inp["tags"]:
                tags.extend(inp["tags"])
        if not queries:
            st.warning("Please enter at least one query.")
            return []
        query_filter = create_filters(list(set(tags)))

        if len(queries) > 1:
            st.warning("Currently only single query is supported. Using the first query.")
            return
    
    elif mode == 'Image Query':
        if not st.session_state.image_upload:
            st.warning("Please upload an image.")
            return []
        from PIL import Image
        image = Image.open(st.session_state.image_upload).convert("RGB")
        queries = [image]
        query_filter = None

    query_vector = model.encode(queries[0]).tolist()
    if query_filter:
        st.session_state.results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=500,
            query_filter=query_filter,
        )
    else:
        st.session_state.results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=500,
        )

    st.session_state.video_list = []
    seen = set()
    for hit in st.session_state.results:
        origin = hit.payload.get("origin")
        if origin not in seen:
            st.session_state.video_list.append(origin)
            seen.add(origin)

    st.session_state.results_sorted = sorted(
        st.session_state.results,
        key=lambda x: (st.session_state.video_list.index(x.payload.get("origin")), x.payload.get("keyframe_id"))
    )


def check_server(collection_name):
    try:
        client.get_collection(collection_name)
        st.success("Server is running and collection exists.")
    except Exception as e:
        st.error(f"Error connecting to server or collection does not exist: {e}")

@st.dialog("Image Details", width='large')
def show_image_details(info, video, image, start_time=0):
    detail_container = st.container(key='detail', border=False)
    with detail_container:
        cols = st.columns([0.5, 0.5])
        with cols[0]:
            st.video(video, start_time=start_time - 2) # start 2 seconds earlier for delay
        with cols[1]:
            st.write(info)
            st.image(image, use_container_width=True)

@st.cache_resource
def load_model():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('clip-ViT-B-32')
    return model

@st.cache_resource
def load_client():
    from qdrant_client import QdrantClient
    client = QdrantClient(host="localhost", port=6333)
    return client

def sort_results():
    return

COLLECTION_NAME = "my_collection"
model = load_model()
client = load_client()
# print(client.get_collection(COLLECTION_NAME))

st.set_page_config(page_title="Visual Browser Search", layout="wide")
# st.title("Visual Browser Search")
st.sidebar.title("Options")

if "next_input_id" not in st.session_state:
    st.session_state.next_input_id = 0

if "tags" not in st.session_state:
    st.session_state.tags = ["Tag1", "Tag2", "Tag3"]

if "inputs" not in st.session_state:
    st.session_state.inputs = [{
        "id": 0,
        "query": "",
        "tags": [],
    }]

if "next_input_id" not in st.session_state:
    st.session_state.next_input_id = 0

if "results" not in st.session_state:
    st.session_state.results = []

if "results_sorted" not in st.session_state:
    st.session_state.results_sorted = []

if "video_list" not in st.session_state:
    st.session_state.video_list = []

if "query_mode" not in st.session_state:
    st.session_state.query_mode = "Text Query"

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
        st.button("🔍 Search", on_click=search_query, args=(st.session_state.query_mode,))
    with cols[1]:
        st.button("➕Add Input", on_click=add_input)
    with cols[2]:
        st.button("Check Server", on_click=check_server, args=(COLLECTION_NAME,), icon=":material/database:")

st.subheader("Search Results") # Dummy results for demonstration
result_widget_container = st.container(height='content', border=True, key='result_widget')
with result_widget_container:
    cols = st.columns([4, 1])
    with cols[0]:
        num_of_cols = st.slider("Number of columns", min_value=10, max_value=20, value=10, step=1)
    with cols[1]:
        st.toggle("Sort by video", on_change=sort_results, key="sort_by_video")

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