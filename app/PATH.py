import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "clip-features-32")
MY_CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "my_feature")
METADATA_PATH = os.path.join(PROJECT_ROOT, "media-info")
MAP_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "map-keyframes")
MY_MAP_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "my-map-keyframes")
KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "keyframes")