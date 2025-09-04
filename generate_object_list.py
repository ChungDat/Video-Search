
import os
import json
from tqdm import tqdm

def get_all_object_labels(root_dir):
    all_labels = set()
    for video_folder in tqdm(os.listdir(root_dir)):
        video_folder_path = os.path.join(root_dir, video_folder)
        if os.path.isdir(video_folder_path):
            for json_file in os.listdir(video_folder_path):
                if json_file.endswith('.json'):
                    json_file_path = os.path.join(video_folder_path, json_file)
                    try:
                        with open(json_file_path, 'r') as f:
                            data = json.load(f)
                            if 'detection_class_entities' in data:
                                all_labels.update(data['detection_class_entities'])
                    except json.JSONDecodeError:
                        print(f"Skipping corrupted JSON file: {json_file_path}")
    return sorted(list(all_labels))

if __name__ == '__main__':
    objects_root = 'samples/objects'
    all_labels = get_all_object_labels(objects_root)
    with open('all_objects.json', 'w') as f:
        json.dump(all_labels, f, indent=4)
    print(f"Found {len(all_labels)} unique object labels. Saved to all_objects.json")
