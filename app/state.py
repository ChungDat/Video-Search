import streamlit as st
import json
from PATH import KEYFRAMES_PATH, MY_KEYFRAMES_PATH

def init_session_state():
    if "collections" not in st.session_state:
        st.session_state.collections = ["my_collection", "my_custom_collection"]

    if "collection_name" not in st.session_state:
        st.session_state.collection_name = st.session_state.collections[0]

    if "next_input_id" not in st.session_state:
        st.session_state.next_input_id = 0
        
    if "inputs" not in st.session_state:
        st.session_state.inputs = [{
            "id": 0,
            "query": "",
        }]

    if "file_content" not in st.session_state:
        st.session_state.file_content = ""

    if "results" not in st.session_state:
        st.session_state.results = []

    if "results_sorted" not in st.session_state:
        st.session_state.results_sorted = []

    if "temporal_results" not in st.session_state:
        st.session_state.temporal_results = []

    if "video_list" not in st.session_state:
        st.session_state.video_list = []

    if "available_tags" not in st.session_state:
        st.session_state.available_tags = json.load(open("all_tags.json", "r", encoding="utf-8"))

    if "available_packs" not in st.session_state:
        st.session_state.available_packs = ["L21", "L22", "L23", "L24", "L25", "L26", "L27", "L28", "L29", "L30", "K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08", "K09", "K10", "K11", "K12", "K13", "K14", "K15", "K16", "K17", "K18", "K19", "K20"]
    
    if "available_videos_per_pack" not in st.session_state:
        st.session_state.available_videos_per_pack = json.load(open("videos_per_pack.json", 'r'))

    if "available_frames_path" not in st.session_state:
        st.session_state.available_frames_path = {"my_collection": KEYFRAMES_PATH, "my_custom_collection": MY_KEYFRAMES_PATH}

    if "frames" not in st.session_state:
        st.session_state.frames = []

    if "start_frame" not in st.session_state:
        st.session_state.start_frame = 0

    if "log" not in st.session_state:
        st.session_state.log = []

    # Load all object labels
    if "all_objects" not in st.session_state:
        st.session_state.all_objects = json.load(open("all_objects.json", "r"))

    if "filter_ignore" not in st.session_state:
        st.session_state.filter_ignore = set()

    if "filter_objects" not in st.session_state:
        st.session_state.filter_objects = []