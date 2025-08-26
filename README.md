# Video-Search

## Setup

1. Clone the repository:
```
git clone https://github.com/ChungDat/Video-Search.git
```
2. Create a new virtual environment, install the requirements.txt
```
conda create --name [environment-name] --file requirements.txt
```
3. Activate the environment
```
conda activate [environment-name]
```
4. Check if qdrant-client is available in python
```
import qdrant-client
print(qdrant-client.__version__)
```
If not, open command prompt, activate the environment and try:
```
pip install qdrant-client
```
5. Download Docker Desktop and run this in command prompt:
```
docker pull qdrant/qdrant
```
After that, run:

* For Windows:
```
docker volume create [volume-name]
docker run -p 6333:6333 -p 6334:6334 --name [container-name] -v [volume-name]:/qdrant/storage qdrant/qdrant
```

## Directory tree

```
Video Search
|-- clip-features-32
|   |-- L21_V001.npy
|   |-- L21_V002.npy
|   ...
|-- keyframes
|   |-- L21_V001
|   |   |-- 001.jpg
|   |   |-- 002.jpg
|   |   ...
|   |-- L21_V002
|   ...
|-- map-keyframes
|   |-- L21_V001.csv
|   |-- L21_V002.csv
|   ...
|-- media-info
|   |-- L21_V001.json
|   |-- L21_V002.json
|   ...
|-- objects
|   |-- L21_V001
|   |   |-- 001.json
|   |   |-- 002.json
|   |-- L21_V002
|   ...
|-- LICENSE
|-- qdrant.ipynb
|-- README.md
|-- requirementx.txt
|-- strlit.py
|-- utils.py
|-- PATH.py
```

## Run the program

1. Ensure Docker container is running
2. Open ```qdrant.ipynb``` and run until cell **Enable Indexing**
3. Open Command Prompt, cd to the directory and run ```streamlit run strlit.py```
