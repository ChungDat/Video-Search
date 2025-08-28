import streamlit as st

def init_session_state():
    if "next_input_id" not in st.session_state:
        st.session_state.next_input_id = 0

    # if "next_submission_id" not in st.session_state:
    #     st.session_state.next_submission_id = 0

    if "tags" not in st.session_state:
        st.session_state.tags = ["Tag1", "Tag2", "Tag3"]

    if "inputs" not in st.session_state:
        st.session_state.inputs = [{
            "id": 0,
            "query": "",
            "tags": [],
        }]

    # if "submissions" not in st.session_state:
    #     st.session_state.submissions = [{
    #         "id": 0,
    #         "video": "",
    #         "frame_index": 0,
    #         "answer": "",
    #     }]

    if "results" not in st.session_state:
        st.session_state.results = []

    if "results_sorted" not in st.session_state:
        st.session_state.results_sorted = []

    if "video_list" not in st.session_state:
        st.session_state.video_list = []

    if "query_mode" not in st.session_state:
        st.session_state.query_mode = "Text Query"

    # if "submission_mode" not in st.session_state:
    #     st.session_state.submission_mode = "KIS_QA"

    if "file_name" not in st.session_state:
        st.session_state.file_name = ""
    
    if "file_content" not in st.session_state:
        st.session_state.file_content = ""