import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "clip-features-32")

# KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "keyframes")
KEYFRAMES_PATH = "https://huggingface.co/datasets/ChungDat/hcm-aic2025-keyframes/resolve/main/"
KEYFRAMES_ROOT = "https://huggingface.co/datasets/ChungDat/hcm-aic2025-keyframes/tree/main"
MAP_KEYFRAMES_PATH = "https://huggingface.co/datasets/ChungDat/hcm-aic2025-additional-data/resolve/main/map-keyframes"

METADATA_PATH = os.path.join(CURRENT_DIR, "media-info")
FPS_PATH = os.path.join(CURRENT_DIR, "video_fps.json")
VIDEOS_PER_PACK_PATH = os.path.join(CURRENT_DIR, "videos_per_pack.json")

MY_CLIP_FEATURES_PATH = os.path.join(PROJECT_ROOT, "my_feature")
MY_MAP_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "my-map-keyframes")
MY_KEYFRAMES_PATH = os.path.join(PROJECT_ROOT, "my-keyframes")

L28_PATH = "https://huggingface.co/datasets/ChungDat/hcm-aic2025-additional-data/resolve/main/video/"
L28_PATH = "https://huggingface.co/datasets/ChungDat/hcm-aic2025-additional-data/resolve/main/video/"