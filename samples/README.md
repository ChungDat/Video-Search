# Data Details

## clip-features-32

Each `.npy` file contains features extracted using the `sentence_transformers` **clip-ViT-B-32** model.  
- Shape: `(n, 512)`, where `n` is the number of keyframes from the corresponding video.  
- The index of each element in the NumPy array matches the index of its corresponding keyframe.

## keyframes

Each folder contains `.jpg` keyframes extracted from the corresponding video.

## map-keyframes

Each `.csv` file contains metadata for the corresponding video, including:  
- FPS of the video  
- Indices of extracted keyframes  
- Timestamps of extraction  
- Frame count at each keyframe  

## media-info

Each `.json` file contains metadata of the corresponding video, including:  
- `author`  
- `channel_id`  
- `channel_url`  
- `description`  
- `keywords`  
- `length`  
- `publish_date`  
- `thumbnail_url`  
- `title`  
- `watch_url`  

## objects

Each folder contains `.json` files, where each file is the output from the [Faster R-CNN model](https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1), listing detected objects for the corresponding image.
