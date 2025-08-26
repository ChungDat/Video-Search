import os
import json
import pandas as pd

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
    time = df.iloc[frame_index]["pts_time"]
    return float(time)

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