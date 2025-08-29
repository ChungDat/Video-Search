import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "clip-features-32")
KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "keyframes")
MAP_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "map-keyframes")
METADATA_PATH = os.path.join(PROJECT_ROOT, "media-info")
FPS_PATH = os.path.join(PROJECT_ROOT, "video_fps.json")

MY_CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "my_feature")
MY_MAP_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "my-map-keyframes")