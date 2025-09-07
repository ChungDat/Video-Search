import streamlit as st
import os
import sys
import json
import json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from PATH import METADATA_PATH, FPS_PATH, L28_PATH
from utils import *
from state import init_session_state

st.set_page_config(page_title="Query Engine", layout='wide')
st.empty()
model = load_model()
client = load_client()
init_session_state()
load_value("collection_name")
load_value("file_content")
disable_scroll_bar()

# Load all object labels
with open("all_objects.json", "r") as f:
    all_objects = json.load(f)

# Custom CSS for a more compact and polished sidebar
st.markdown('''
<style>
    /* General sidebar enhancements */
    [data-testid="stSidebar"] {
        width: 350px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="stSidebar"] .stButton button {
        margin-top: 0.5em;
    }
    [data-testid="stSidebar"] .stExpander {
        border: none;
    }
    [data-testid="stSidebar"] .stExpander summary {
        padding: 0.5rem 0;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.8rem;
        padding-top: 0;
        margin-top: 0;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-size: 1.4rem;
    }
    [data-testid="stSidebar"] .stTabs [data-testid="stMarkdownContainer"] {
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] .stTextArea textarea {
        height: 80px !important;
    }
</style>
''', unsafe_allow_html=True)


###################
# SIDEBAR - CONTROLS
###################
with st.sidebar:
    st.title("Search Tools")
    
    # --- Combined Query Section ---
    st.header("Combined Query")

    # --- Text Query Input ---
    if not st.session_state.inputs:
        st.button("➕ Add Query", on_click=add_input, width="stretch")
    else:
        query_tabs = st.tabs([f"Query {i+1}" for i, inp in enumerate(st.session_state.inputs)])
        for i, (tab, inp) in enumerate(zip(query_tabs, st.session_state.inputs)):
            with tab:
                st.session_state.inputs[i]["query"] = st.text_area(
                    f"query_content_{i+1}",
                    key=f"query_{inp['id']}",
                    on_change=update_input_query,
                    args=(i,),
                    label_visibility="collapsed",
                    placeholder=f"Enter query text {i+1}..."
                )
                if len(st.session_state.inputs) > 1:
                    st.button(
                        "Remove this query",
                        key=f"remove_input_{inp['id']}",
                        on_click=remove_input,
                        args=(inp["id"],),
                        width="stretch"
                    )
        
        cols = st.columns(2)
        cols[0].button("➕ Add Query", on_click=add_input, use_container_width=True)
        cols[1].button("Clear All", on_click=clear_input, icon=":material/clear_all:", use_container_width=True)

    # --- Image Query Input ---
    st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"], key="image_upload")

    # --- Filter Section ---
    st.header("Filters")
    st.multiselect("Packs", options=st.session_state.available_packs, key="filter_packs", help="Select video packs to search within.")
    
    filter_tags = []
    if st.session_state.filter_packs:
        for pack in st.session_state.filter_packs:
            filter_tags.extend(st.session_state.available_tags.get(pack, []))
        filter_tags = sorted(list(set(filter_tags)))
    
    st.multiselect("Tags", options=filter_tags, key="filter_tags", help="Filter by tags within the selected packs.")
    st.multiselect("Objects", options=all_objects, key="filter_objects", help="Filter by objects detected in the keyframes.")
    
    with st.expander("Pack Descriptions"):
        st.text('''L21: tin tức, 60 giây sáng
L22: tin tức, 60 giây chiều
L23: thể thao, đua xe đạp
L24: thể thao, lăn sư rồng
L25: học tập, ôn thi thpt
L26: ẩm thực, món ngon mỗi ngày
L27: du lịch văn hóa, VN đi là ghiền
L28: du lịch văn hóa, tản mạn Mê Kông
L29: du lịch văn hóa, đôi mắt Mê Kông
L30: đời sống, lan toả năng lượng tích cực''')
    
    # --- Search Execution ---
    cols = st.columns(2)
    cols[0].button("🔍 Search", on_click=search_query, args=(model, client, st.session_state.collection_name, 300), type="primary", use_container_width=True)
    cols[1].button("Save Log", on_click=save_log, use_container_width=True)

    st.divider()

    # --- Submission Section ---
    st.header("Submission")
    
    cols = st.columns([3, 1])
    cols[0].text_input('File name', key='file_name', placeholder="e.g., results_01")
    cols[1].write("`.csv`")
    
    st.text_area(
        "Answers",
        "Answers",
        key="_file_content",
        on_change=store_value,
        args=("file_content",),
        placeholder="Add answers for your submission file here...",
        height=100
    )
    
    cols = st.columns(2)
    cols[0].button("Submit", key="submit_button", on_click=submit, icon=":material/assignment:", use_container_width=True)
    cols[1].button("Clear", key="clear_submission_button", on_click=clear_submission, icon=":material/clear_all:", use_container_width=True)


###################
# MAIN AREA - SCROLLABLE RESULTS
###################
with st.container():
    st.header("Search Results")

    # Result controls
    cols = st.columns([2, 1, 1])
    with cols[0]:
        num_of_cols = st.slider("Columns", min_value=2, max_value=15, value=5, step=1)
    with cols[1]:
        st.toggle("Sort by video", key="sort_by_video")
    with cols[2]:
        if st.session_state.results:
            st.write(f"**{len(st.session_state.results)} results**")

    # Results display
    if not st.session_state.sort_by_video:
        if st.session_state.results:
            cols = st.columns(num_of_cols)
            for i, hit in enumerate(st.session_state.results):
                pack = hit.payload.get("pack")
                video = hit.payload.get("video")
                frame_index = hit.payload.get("frame_index")
                frame = hit.payload.get("frame")
                origin = pack + '_' + video
                metadata = get_video_metadata(METADATA_PATH, origin, ["watch_url"])
                start_time = get_frame_start_time(FPS_PATH, origin, frame_index)
                frame_path = os.path.join(st.session_state.available_frames_path[st.session_state.collection_name], origin, frame)
                if pack == "L28":
                    video_data = os.path.join(L28_PATH, origin + ".mp4")
                else:
                    video_data = get_frame_url(FPS_PATH, origin, metadata)

                with cols[i % num_of_cols]:
                    st.image(frame_path, width="stretch")
                    st.caption(f"{origin} - {start_time}s")
                    if st.button("Details", key=f"image_{i}", width="stretch"):
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
            st.info("No results to display. Run a search to see results here.")
    else:
        if st.session_state.results:
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
                st.subheader(f"{i + 1}. {candidate}")
                cols = st.columns(num_of_cols)
                for j, hit in enumerate(video_hits):
                    pack = hit.payload.get("pack")
                    video = hit.payload.get("video")
                    frame = hit.payload.get("frame")
                    frame_index = hit.payload.get("frame_index")
                    origin = pack + '_' + video
                    metadata = get_video_metadata(METADATA_PATH, origin, ["watch_url"])
                    start_time = get_frame_start_time(FPS_PATH, origin, frame_index)
                    frame_path = os.path.join(st.session_state.available_frames_path[st.session_state.collection_name], origin, frame)
                    if hit.payload.get("pack") == "L28":
                        video_data = os.path.join(L28_PATH, origin + ".mp4")
                    else:
                        video_data = get_frame_url(FPS_PATH, origin, metadata)

                    with cols[j % num_of_cols]:
                        st.image(frame_path, width="stretch")
                        st.caption(f"{start_time}s")
                        if st.button("Details", key=f"image_{candidate}_{j}", width="stretch"):
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
                st.divider()
        else:
            st.info("No results to display. Run a search to see results here.")