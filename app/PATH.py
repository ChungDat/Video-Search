import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "clip-features-32")

# KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "keyframes")
KEYFRAMES_PATH = "https://huggingface.co/datasets/ChungDat/hcm-aic2025-keyframes/resolve/main/"
MAP_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "map-keyframes")
METADATA_PATH = os.path.join(CURRENT_DIR, "media-info")
FPS_PATH = os.path.join(CURRENT_DIR, "video_fps.json")

MY_CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "my_feature")
MY_MAP_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "my-map-keyframes")
MY_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "my-keyframes")

L28_PATH = os.path.join(PROJECT_ROOT, "Videos_L28_a", "video")