import streamlit as st
import csv

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

def search_query(mode: str, model: 'SentenceTransformer', client: 'QdrantClient', collection_name: str):
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
            collection_name=collection_name,
            query_vector=query_vector,
            limit=200,
            query_filter=query_filter,
        )
    else:
        st.session_state.results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=200,
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


def check_server(client: 'QdrantClient', collection_name: str):
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
