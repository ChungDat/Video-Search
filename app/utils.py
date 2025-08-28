from __future__ import annotations # for type hint
import pandas as pd
import streamlit as st
import os
import csv
import json

##########################
# PROCESS VIDEO FUNCTION #
##########################
def get_video_pack_files(folder: str, video_pack: str) -> list[str]:
    """
    Get all files in the folder that start with the video pack name.
    Args:
        folder (str): The folder to search in.
        video_pack (str): The video pack name to filter files by.
    Returns:
        list[str]: A list of file names that start with the video pack name."""
    
    if not os.path.exists(folder):
        return []
    
    files = []
    for file_name in os.listdir(folder):
        if file_name.startswith(video_pack):
            files.append(file_name)
    return files

def get_video_metadata(folder: str, video: str, selected_keys: list[str]) -> dict:
    """
    Get metadata from a JSON file.
    Args:
        folder (str): The folder where the JSON files are located.
        video (str): The name of the video.
        selected_keys (list[str]): The keys to extract from the metadata.
        Available keys: ['author', 'channel_id', 'channel_url', 'description', 'keywords', 
        'length', 'publish_date', 'thumbnail_url', 'title', 'watch_url']
    Returns:
        dict: The metadata as a dictionary."""
    
    metadata_path = os.path.join(folder, video + ".json")
    if not os.path.exists(metadata_path):
        return {}
    metadata = json.load(open(metadata_path, "r", encoding="utf-8"))
    return {key: metadata[key] for key in selected_keys if key in metadata}

def get_keyframe_start_time(folder: str, video: str, frame_index: int = 0) -> float:
    """
    Get the start time of a specific frame from the metadata.
    Args:
        folder (str): The folder where the map-keyframes files are stored.
        video (str): The name of the video.
        frame_index (int): The index of the keyframe.
    Returns:
        float: The start time of the keyframe in seconds."""
    
    df = pd.read_csv(os.path.join(folder, video + ".csv"))
    try:
        time = df.iloc[frame_index - 1]["pts_time"] # Offset by -1 because the first line of the csv is the header
        return float(time)
    except IndexError:
        print(f"Frame index {frame_index} out of range for video {video}. Returning 0.0.")

def get_keyframe_url(folder: str, video: str, metadata: dict, frame_index: int = 0) -> str:
    """
    Get the URL to youtube of a specific frame from the metadata.
    Args:
        folder (str): The folder where the map-keyframes files are stored.
        video (str): The name of the video.
        metadata (dict): The metadata dictionary containing video information.
        frame_index (int): The index of the keyframe. If 0, the url will point to the start of the video.
    Returns:
        str: The URL of the keyframe image."""
    
    time = get_keyframe_start_time(folder, video, frame_index)
    url = metadata["watch_url"] + "&t=" + str(int(time))
    return url

def get_frame_url(video: str, metatdata: dict, fps: float, frame_index: int = 0) -> str:
    """
    Get the URL to youtube of a specific frame from the metadata.
    Args:
        video (str): The name of the video.
        metatdata (dict): The metadata dictionary containing video information.
        fps (float): The frames per second of the video.
        frame_index (int): The index of the keyframe.
    Returns:
        str: The URL of the keyframe image."""
    
    time = frame_index / fps
    url = metatdata["watch_url"] + "&t=" + str(int(time))
    return url

def get_video_fps(file: str, video: str) -> float:
    """
    Get the frames per second (FPS) of a video from a .json file.
    Args:
        file (str): The path to the .json file containing videos information.
        video (str): The name of the video.
    Returns:
        float: The frames per second of the video."""
    
    if not os.path.exists(file):
        return 0.0
    fps = json.load(file)
    if video not in fps.keys():
        return 0.0
    return float(fps[video])

def get_keyframe_image_path(folder: str, video: str, frame_index: int) -> str:
    """
    Get the path to the keyframe image.
    Args:
        folder (str): The folder where the keyframes are stored.
        video (str): The name of the video.
        frame_index (int): The index of the frame.
    Returns:
        str: The path to the keyframe image."""
    
    if frame_index < 10:
        frame_index = "00" + str(frame_index)
    elif frame_index < 100:
        frame_index = "0" + str(frame_index)
    else:
        frame_index = str(frame_index)

    path = os.path.join(folder, video, frame_index + ".jpg")
    if not os.path.exists(path):
        return ""
    return path

#######################
# STREAMLIT FUNCTIONS #
#######################

def add_input() -> None:
    st.session_state.next_input_id += 1
    st.session_state.inputs.append({
        "id": st.session_state.next_input_id,
        "query": "",
        "tags": [],
    })

def add_submission() -> None:
    st.session_state.next_submission_id += 1
    st.session_state.submissions.append({
        "id": st.session_state.next_submission_id,
        "video": "",
        "frame_index": 0,
        "answer": "",
    })

def remove_input(id) -> None:
    if len(st.session_state.inputs) > 1:
        st.session_state.inputs = [inp for inp in st.session_state.inputs if inp["id"] != id]

def remove_submission(id) -> None:
    if len(st.session_state.submissions) > 1:
        st.session_state.submissions = [sub for sub in st.session_state.submissions if sub["id"] != id]

def update_input_query(i) -> None:
    st.session_state.inputs[i]["query"] = st.session_state[f"query_{st.session_state.inputs[i]['id']}"]

def update_submission_video(i) -> None:
    st.session_state.submissions[i]["video"] = st.session_state[f"video_{st.session_state.submissions[i]['id']}"]

def update_input_tags(i) -> None:
    st.session_state.inputs[i]["tags"] = st.session_state[f"tag_{st.session_state.inputs[i]['id']}"]

def update_submission_frame_index(i) -> None:
    st.session_state.submissions[i]["frame_index"] = st.session_state[f"frame_index_{st.session_state.submissions[i]['id']}"]

def update_submission_answer(i) -> None:
    st.session_state.submissions[i]["answer"] = st.session_state[f"answer_{st.session_state.submissions[i]['id']}"]

def submit():
    # lines = [line.strip() for line in st.session_state.file_content.splitlines() if line.strip()]
    # rows = [line.split(",") for line in lines]
    # rows = [[col.strip() for col in row] for row in rows]

    # df = pd.DataFrame(rows, columns=["Video", "Frame Index"])

    # # Save to disk
    # df.to_csv(st.session_state.file_name + '.csv', index=False)

    # st.success(f"Saved CSV to {st.session_state.file_name + '.csv'}")
    # st.dataframe(df)

    if not os.path.exists('submission'):
        os.makedirs('submission')

    with open(os.path.join('submission', st.session_state.file_name + ".csv"), "w", encoding="utf-8") as f:
        for line in st.session_state.file_content.splitlines():
            if line.strip():  # skip empty lines
                f.write(line.strip() + "\n")
    st.success("Success write file to " + os.path.join('submission', st.session_state.file_name + ".csv"))

def clear_input():
    st.session_state.next_input_id += 1
    st.session_state.inputs = [{
            "id": st.session_state.next_input_id,
            "query": "",
            "tags": [],
        }]

def clear_submission():
    st.session_state.file_name = ""
    st.session_state.file_content = ""

@st.cache_data
def create_filters(tags) -> models.Filter | None:
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

def search_query(mode: str, model: SentenceTransformer, client: QdrantClient, collection_name: str) -> None:
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


def check_server(client: QdrantClient, collection_name: str) -> None:
    try:
        client.get_collection(collection_name)
        st.success("Server is running and collection exists.")
    except Exception as e:
        st.error(f"Error connecting to server or collection does not exist: {e}")

@st.dialog("Image Details", width='large')
def show_image_details(info, video, image, start_time=0) -> None:
    detail_container = st.container(key='detail', border=False)
    with detail_container:
        cols = st.columns([0.5, 0.5])
        with cols[0]:
            st.video(video, start_time=start_time - 2) # start 2 seconds earlier for delay
        with cols[1]:
            st.write(info)
            st.image(image, use_container_width=True)

@st.cache_resource
def load_model() -> SentenceTransformer:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('clip-ViT-B-32')
    return model

@st.cache_resource
def load_client() -> QdrantClient:
    from qdrant_client import QdrantClient
    client = QdrantClient(host="localhost", port=6333)
    return client
