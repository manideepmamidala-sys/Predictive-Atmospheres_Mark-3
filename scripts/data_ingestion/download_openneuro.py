import urllib.request
import json
import os
import sys

# Target directory
target_dir = "data/paper_data/emotion_ratings"
os.makedirs(target_dir, exist_ok=True)

# Dataset ID and snapshot
dataset_id = "ds004872"
snapshot = "1.0.1"

# API endpoint for file tree
api_url = f"https://openneuro.org/crn/datasets/{dataset_id}/snapshots/{snapshot}/files"

print(f"Fetching file list from {api_url}...")
req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        file_tree = json.loads(response.read().decode())
except Exception as e:
    print(f"Error fetching file list: {e}")
    sys.exit(1)

def download_file(url, local_path):
    print(f"Downloading {local_path}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Recursively download files
def process_tree(node, current_path=""):
    if isinstance(node, list):
        for item in node:
            process_tree(item, current_path)
    elif isinstance(node, dict):
        if 'urls' in node and node['urls']:
            # It's a file
            file_name = node['filename']
            file_url = node['urls'][0]
            
            # Create subdirectories if necessary
            full_local_path = os.path.join(target_dir, current_path, file_name)
            os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
            
            download_file(file_url, full_local_path)
        elif 'directory' in node and 'files' in node:
            # It's a directory
            dir_name = node['directory']
            process_tree(node['files'], os.path.join(current_path, dir_name))

process_tree(file_tree)
print("Download complete!")
