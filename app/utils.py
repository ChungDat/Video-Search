import pandas as pd
import streamlit as st
import numpy as np
import os
import json
import cv2
import time
from cap_from_youtube import cap_from_youtube
from sentence_transformers import SentenceTransformer
from qdrant_client.http import models
from qdrant_client import QdrantClient
from dotenv import load_dotenv
from PATH import METADATA_PATH
from collections import Counter
from collections import defaultdict

##########################
# PROCESS VIDEO FUNCTION #
##########################
def get_video_pack_files(folder: str, video_pack: str) -> list[str]:
    """
    Get all files in the folder that start with the video pack name.
    Args:
        folder (str): Folder to search in.
        video_pack (str): Video pack name to filter files by.
    Returns:
        list[str]: A list of file names that starts with video_pack."""
    
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
        folder (str): Folder where JSON files are located.
        video (str): Name of video.
        selected_keys (list[str]): Keys to extract from the metadata.
            Available keys: ['author', 'channel_id', 'channel_url', 'description', 'keywords', 
            'length', 'publish_date', 'thumbnail_url', 'title', 'watch_url']
    Returns:
        dict: Metadata as a dictionary."""
    
    metadata_path = os.path.join(folder, video + ".json")
    if not os.path.exists(metadata_path):
        return {}
    metadata = json.load(open(metadata_path, "r", encoding="utf-8"))
    return {key: metadata[key] for key in selected_keys if key in metadata}

def get_video_fps(file: str, video: str) -> float:
    """
    Get the frames per second (FPS) of a video from a .json file.
    Args:
        file (str): Path to the .json file containing videos fps.
        video (str): Name of video.
    Returns:
        float: Frames per second of video."""
    
    if not os.path.exists(file):
        return 0.0
    fps_data = json.load(open(file, 'r'))
    if video not in fps_data.keys():
        return 0.0
    return float(fps_data[video])

def get_video_duration(video_name: str) -> int:
    """Gets the duration of a video in seconds."""

    metadata = get_video_metadata(METADATA_PATH, video_name, ["length"])
    return metadata.get("length", 0)

def get_keyframe_data(folder: str, video: str) -> pd.DataFrame:
    """
    Get timestamp, fps, frame_index of each keyframe in video.

    Args:
        folder (str): Folder where map-keyframes files are stored.
        video (str): Name of video.
    Returns:
        pd.DataFrame: A DataFrame containing timestamp, fps, frame_index of each keyframe in video.
    """
    df = pd.read_csv(os.path.join(folder, video + ".csv"))
    return df

def get_object_data(folder: str, video: str, frame_n: str) -> list:
    """
    Get object data from a JSON file.

    Args:
        folder (str): Folder where object files are stored.
        video (str): Name of video.
        frame_n (str): Name of the keyframe file (e.g., '001.jpg').
    Returns:
        list: A list of detected object entities.
    """
    json_path = os.path.join(folder, video, frame_n.replace('.jpg', '.json'))
    if not os.path.exists(json_path):
        return []
    with open(json_path, 'r') as f:
        data = json.load(f)
        return data.get("detection_class_entities", [])

def get_keyframe_image_path(folder: str, video: str, frame_n: int) -> str:
    """
    Get path to keyframe.

    Args:
        folder (str): Folder where keyframes are stored.
        video (str): Name of video.
        frame_n (int): The n-th keyframe.
    Returns:
        str: Path to keyframe.
    """
    
    if frame_n < 10:
        frame_n = "00" + str(frame_n)
    elif frame_n < 100:
        frame_n = "0" + str(frame_n)
    else:
        frame_n = str(frame_n)

    path = os.path.join(folder, video, frame_n + ".jpg")
    if not os.path.exists(path):
        return ""
    return path

def get_keyframe_index(folder: str, video: str, frame_n: int) -> int:
    """
    Get the actual frame index of n-th keyframe.

    Args:
        folder (str): Folder where map-keyframes files are stored.
        video (str): Name of video.
        frame_n (int): N-th keyframe of video.
    Returns:
        int: The actual frame index of n-th keyframe.
    """
    df = pd.read_csv(os.path.join(folder, video + ".csv"))
    try:
        frame_index = df.iloc[frame_n - 1]["frame_idx"] # Offset by -1 because the first line of the csv is the header
        return int(frame_index)
    except IndexError:
        print(f"{frame_n} keyframe does not exists in {video}.csv. Returning 0.")

def get_frame_start_time(fps_file: str, video: str, frame_index: float) -> float:
    """
    Get timestamp of frame in video.

    Agrs:
        fps_file (str): Path to the .json file containing videos fps.
        video (str): Name of video.
        frame_index (int): Frame index in video.
    Returns:
        float: Timestamp of frame.
    """
    fps = get_video_fps(fps_file, video)
    if fps == 0:
        return 0.0
    return frame_index / fps
        
def get_frame_url(file: str, video: str, metadata: dict, frame_index: int = 0) -> str:
    """
    Get the URL to youtube of a specific frame from metadata.
    Args:
        file (str): Path to the .json file containing videos fps.
        video (str): Name of video.
        metatdata (dict): Metadata dictionary containing video information.
        frame_index (int): Index of the frame
    Returns:
        str: URL that starts video at frame.
    """
    
    time = get_frame_start_time(file, video, frame_index)
    url = metadata["watch_url"] + "&t=" + str(int(time))
    return url

def sample_frames(video_path: str, fromYoutube: bool, start_timestamp_in_s: int, end_timestamp_in_s: int, step: int, scale: float) -> tuple[list[np.ndarray], int]:
    start_time = time.time()
    if fromYoutube:
        cap = cap_from_youtube(video_path)
    else:
        cap = cv2.VideoCapture(video_path)
    end_time = time.time()
    st.write(f"Open VideoCapture time: {end_time - start_time}")

    VID_FPS = cap.get(cv2.CAP_PROP_FPS)
    VID_FRAME_COUNT = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    start_frame = start_timestamp_in_s * VID_FPS
    end_frame = end_timestamp_in_s * VID_FPS

    frames = []
    count = 0
    current_frame = start_frame
    start_time = time.time()
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    end_time = time.time()
    st.write(f"Set frame position time: {end_time - start_time}")
    st.write(f"Start frame: {start_frame} | Frame count: {VID_FRAME_COUNT}")
    start_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if (count % step == 0):
            frame = cv2.resize(frame, dsize=None, fx=scale, fy=scale)
            frames.append(frame)
        count += 1
        current_frame += 1
        if current_frame > end_frame:
            break
    cap.release()
    end_time = time.time()
    st.write(f"Extract frames time: {end_time - start_time}")
    return frames, VID_FPS

def sample_frames_2(video_path: str, fromYoutube: bool, start_timestamp_in_s: int, end_timestamp_in_s: int, step: int, scale: float) -> tuple[list[np.ndarray], int]:
    start_time = time.time()
    if fromYoutube:
        cap = cap_from_youtube(video_path)
    else:
        cap = cv2.VideoCapture(video_path)
    end_time = time.time()
    st.write(f"Open VideoCapture time: {end_time - start_time}")

    VID_FPS = cap.get(cv2.CAP_PROP_FPS)
    VID_FRAME_COUNT = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    start_frame = start_timestamp_in_s * VID_FPS
    end_frame = end_timestamp_in_s * VID_FPS

    frames = []
    current_frame = 0
    start_time = time.time()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if (current_frame < start_frame):
            current_frame += 1
            continue
        if current_frame > end_frame:
            break
        if (current_frame % step == 0):
            frame = cv2.resize(frame, dsize=None, fx=scale, fy=scale)
            frames.append(frame)
        current_frame += 1
    cap.release()
    end_time = time.time()
    st.write(f"Extract frames time: {end_time - start_time}")
    return frames, VID_FPS


#######################
# STREAMLIT FUNCTIONS #
#######################

def add_input() -> None:
    st.session_state.next_input_id += 1
    st.session_state.inputs.append({
        "id": st.session_state.next_input_id,
        "query": "",
    })

def remove_input(id) -> None:
    if len(st.session_state.inputs) > 1:
        st.session_state.inputs = [inp for inp in st.session_state.inputs if inp["id"] != id]

def update_input_query(i) -> None:
    st.session_state.inputs[i]["query"] = st.session_state[f"query_{st.session_state.inputs[i]['id']}"]

def submit() -> None:
    if not os.path.exists('submission'):
        os.makedirs('submission')
    if not st.session_state.file_name or not st.session_state.file_content:
        st.warning("Nothing to submit")
        return

    with open(os.path.join('submission', st.session_state.file_name + ".csv"), "w", encoding="utf-8") as f:
        for line in st.session_state.file_content.splitlines():
            if line.strip():  # skip empty lines
                f.write(line.strip() + "\n")
    st.success("Success write file to " + os.path.join('submission', st.session_state.file_name + ".csv"))

def clear_input() -> None:
    st.session_state.next_input_id += 1
    st.session_state.inputs = [{
        "id": st.session_state.next_input_id,
        "query": "",
    }]

def add_answer(answer: str) -> None:
    st.session_state.file_content += answer + "\n"
    
def clear_submission() -> None:
    st.session_state.file_name = ""
    st.session_state.file_content = ""

def store_value(key: str) -> None:
    st.session_state[key] = st.session_state["_" + key]

def load_value(key: str) -> None:
    st.session_state["_" + key] = st.session_state[key]

@st.cache_data
def create_filter_conditions(packs: list[str], tags: list[str]) -> list[models.FieldCondition] | None:
    """
    Create conditions to search for videos in packs with specific tags.

    Agrs:
        packs (list[str]): A list of selected packs.
        tags (list[str]): A list of selected tags.
    Returns:
        list[models.FieldCondition] | None: A lsit of conditions if packs or tags is provided. Returns None otherwise.
    """

    if not tags and not packs:
        return None
    conditions = []
    if packs:
        conditions.append(
            models.FieldCondition(
                key="pack",
                match=models.MatchAny(any=packs)
            )
        )
    if tags:
        for tag in tags:
            conditions.append(
                models.FieldCondition(
                    key="tags",
                    match=models.MatchValue(value=tag)
                )
            )
    if not conditions:
        return None
    return conditions

@st.cache_data
def create_ignore_condition(origins: set[str]) -> list[models.FieldCondition] | None:
    """
    Create conditions to ignore when searching for videos.

    Agrs:
        origins (list[str]): A list of videos to ignore.
    Returns:
        list[models.FieldCondition] | None: A list of conditions if origins is provided. Returns None otherwise.
    """

    if not origins:
        return None
    conditions = []
    for origin in origins:
        pack, video = origin.split('_')
        conditions.append(
            models.Filter(
                must=[
                    models.FieldCondition(
                        key="pack",
                        match=models.MatchValue(value=pack)
                    ),
                    models.FieldCondition(
                        key="video",
                        match=models.MatchValue(value=video)
                    ),
                ]
            )
        )
    if not conditions:
        return None
    return conditions

def search_query(model: SentenceTransformer, client: QdrantClient, collection_name: str, limit: int = 200) -> None:
    """Perform search based on the current inputs and update results in session state."""
    text_queries = []
    for inp in st.session_state.inputs:
        if inp["query"]:
            text_queries.append(inp["query"])

    image_query = st.session_state.get("image_upload")
    query_condition = create_filter_conditions(st.session_state.filter_packs, st.session_state.filter_tags)
    ignore_condition = create_ignore_condition(st.session_state.filter_ignore)

    if not text_queries and not image_query and not query_condition and not st.session_state.filter_objects:
        st.warning("Please enter a query or select a filter.")
        return

    query_vectors = []
    log_query = []

    if text_queries:
        if len(text_queries) > 1:
            st.warning("Currently only single text query is supported. Using the first query.")
        text_vector = model.encode(text_queries[0]).tolist()
        query_vectors.append(text_vector)
        log_query.append(text_queries[0])

    if image_query:
        from PIL import Image
        image = Image.open(image_query).convert("RGB")
        image_vector = model.encode(image).tolist()
        query_vectors.append(image_vector)

    if query_vectors:
        if len(query_vectors) > 1:
            final_query_vector = np.mean(query_vectors, axis=0).tolist()
        else:
            final_query_vector = query_vectors[0]
        
        st.session_state.results = client.search(
            collection_name=collection_name,
            query_vector=final_query_vector,
            limit=limit,
            query_filter=models.Filter(must=query_condition, must_not=ignore_condition),
        )
    else: # No query, just filters
        st.session_state.results, _ = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(must=query_condition, must_not=ignore_condition),
            limit=limit
        )

    # Post-filter by objects
    if st.session_state.filter_objects:
        filtered_results = []
        # If no other filters are applied, we need to get all points first
        if not query_condition and not query_vectors:
            all_results, _ = client.scroll(collection_name=collection_name, limit=10000) # A high limit to get all points
            st.session_state.results = all_results

        for hit in st.session_state.results:
            video_name = hit.payload.get("pack") + '_' + hit.payload.get("video")
            frame_file = hit.payload.get("frame")
            object_data = get_object_data("objects", video_name, frame_file)
            if all(obj in object_data for obj in st.session_state.filter_objects):
                filtered_results.append(hit)
        st.session_state.results = filtered_results

    st.session_state.origin_rank = []
    seen = set()
    for hit in st.session_state.results:
        pack = hit.payload.get("pack")
        video = hit.payload.get("video")
        origin = pack + '_' + video
        if origin not in seen:
            st.session_state.origin_rank.append(origin)
            seen.add(origin)
    st.session_state.results_sorted = sorted(
        st.session_state.results,
        key=lambda x: (st.session_state.origin_rank.index(x.payload.get("pack") + '_' + x.payload.get("video")), x.payload.get("frame_index"))
    )
    st.session_state.log.append({"collection": collection_name, "query": log_query, "filter_packs": st.session_state.filter_packs, "filter_tags": st.session_state.filter_tags, "filter_objects": st.session_state.filter_objects})
    
def rerank_temporal_queries(results):
    # Step 1: collect payloads per query for frequency
    payloads_per_query = []
    for resp in results:
        query_payloads = {
            p.payload.get("pack") + '_' + p.payload.get("video")
            for p in resp.points
        }
        payloads_per_query.append(query_payloads)

    freq = Counter()
    for query_set in payloads_per_query:
        freq.update(query_set)

    # Step 2: group all points by payload, storing query index too
    groups = defaultdict(list)
    for q_idx, resp in enumerate(results):
        for p in resp.points:
            key = p.payload.get("pack") + '_' + p.payload.get("video")
            if groups[key] and groups[key][0][0] != 0:
                continue
            groups[key].append((q_idx, p))  # store query index

    # Step 3: sort groups by frequency, then best score
    def group_sort_key(item):
        payload, pts = item
        return (
            -freq[payload],                        # more queries first
            -max(p.score for _, p in pts)          # best score in group
        )
    
    sorted_groups = sorted(groups.items(), key=group_sort_key)
    st.session_state.origin_rank = []
    seen = set()
    for origin, pts in sorted_groups:
        if origin not in seen:
            seen.add(origin)
            st.session_state.origin_rank.append(origin)

    # Step 4: sort inside each group by query index first, then score
    final_list = []
    for payload, pts in sorted_groups:
        pts_sorted = sorted(
            pts,
            key=lambda x: (x[0], -x[1].score)  # query index ascending, score descending
        )
        final_list.extend(p for _, p in pts_sorted)

    return final_list

def temporal_search_query(model: SentenceTransformer, client: QdrantClient, collection_name: str, limit: int = 200) -> None:
    """Perform search based on the current inputs and update results in session state."""
    text_queries = []
    for inp in st.session_state.inputs:
        if inp["query"]:
            text_queries.append(inp["query"])

    image_query = st.session_state.get("image_upload")
    query_condition = create_filter_conditions(st.session_state.filter_packs, st.session_state.filter_tags)
    ignore_condition = create_ignore_condition(st.session_state.filter_ignore)

    if not text_queries and not image_query:
        st.warning("Please enter a query.")
        return

    query_vectors = []
    log_query = []

    for text_query in text_queries:
        text_vector = model.encode(text_query).tolist()
        query_vectors.append(text_vector)
        log_query.append(text_query)

    # if image_query:
    #     from PIL import Image
    #     image = Image.open(image_query).convert("RGB")
    #     image_vector = model.encode(image).tolist()
    #     query_vectors.append(image_vector)

    search_queries = [
        models.QueryRequest(query=query_vector, filter=models.Filter(must=query_condition, must_not=ignore_condition), limit=limit, with_payload=True) for query_vector in query_vectors
    ]

    results = client.query_batch_points(
        collection_name=collection_name,
        requests=search_queries,
    )

    # # Post-filter by objects
    # if st.session_state.filter_objects:
    #     filtered_results = []

    #     for result in results:
    #         filtered_result = []
    #         for hit in result:
    #             video_name = hit.payload.get("pack") + '_' + hit.payload.get("video")
    #             frame_file = hit.payload.get("frame")
    #             object_data = get_object_data("objects", video_name, frame_file)
    #             if all(obj in object_data for obj in st.session_state.filter_objects):
    #                 filtered_result.append(hit)
    #         filtered_results.append(filtered_result)
    #     st.session_state.results = filtered_results

    st.session_state.temporal_results = rerank_temporal_queries(results)

    st.session_state.log.append({"collection": collection_name, "query": log_query, "filter_packs": st.session_state.filter_packs, "filter_tags": st.session_state.filter_tags, "filter_objects": st.session_state.filter_objects})

def save_log() -> None:
    with open("log.json", 'w') as f:
        json.dump(st.session_state.log, f)
        st.success("Successfully dump log to log.json")

def check_server(client: QdrantClient, collection_name: str) -> None:
    try:
        client.get_collection(collection_name)
        st.success("Server is running and collection exists.")
    except Exception as e:
        st.error(f"Error connecting to server or collection does not exist: {e}")

@st.dialog("Details", width='large', on_dismiss="rerun")
def show_details(origin: str, frame_index: int, frame: str, data: str, frame_path: str, fps_file: str, video_name: str, start_time: float = 0) -> None:
    st.write(
        """<style>
        .stDialog *[role="dialog"] {
            width: 75%;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    info = f"Video: {origin}\tFrame index: {frame_index}\tFrame name: {frame}"
    detail_container = st.container(key='detail_container', border=False)
    st.session_state.fps = get_video_fps(fps_file, video_name)
    
    # Initialize calculator_index with a default value
    calculator_index = int(start_time * st.session_state.fps)

    with detail_container:
        cols = st.columns([0.65, 0.35])
        with cols[0]:
            st.video(data, start_time=start_time)
            duration = get_video_duration(video_name)
            if duration > 0:
                selected_seconds = st.slider("Select time", 0, duration, int(start_time))
                
                minutes = selected_seconds // 60
                seconds = selected_seconds % 60
                
                sub_cols = st.columns(2)
                with sub_cols[0]:
                    st.write(f"Selected Time: {minutes:02d}:{seconds:02d} | FPS: {st.session_state.fps:.2f}")
                    
                    # Update calculator_index based on slider
                    calculator_index = int(selected_seconds * st.session_state.fps)
                    st.write(f"Frame Index: {calculator_index}")
                with sub_cols[1]:
                    if st.button("Ignore this video"):
                        st.session_state.filter_ignore.add(origin)

        with cols[1]:
            st.image(frame_path, use_container_width=True)
            if info:
                st.text(info)
            sub_cols = st.columns(2)
            with sub_cols[0]:
                st.button(label="Use Calculator Index", key="calculator_index_button", on_click=add_answer, args=((f"{origin}, {calculator_index}"),))

            with sub_cols[1]:
                st.button(label="Use Image Index", key="image_index_button", on_click=add_answer, args=((f"{origin}, {int(frame_index)}"),))

@st.cache_resource
def load_model() -> SentenceTransformer:
    
    model = SentenceTransformer('clip-ViT-B-32')
    return model

@st.cache_resource
def load_client() -> QdrantClient:
    load_dotenv()
    client = QdrantClient(
        url="https://9bf65806-b1f1-498b-b309-079694a5a23b.us-east4-0.gcp.cloud.qdrant.io", 
        api_key=os.getenv("QDRANT_TOKEN_READ"),
        timeout=60,
    )
    return client