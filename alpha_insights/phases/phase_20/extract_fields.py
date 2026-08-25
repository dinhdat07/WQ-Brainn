import json
import requests
import os

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

def get_datasets(limit=100, offset=0):
    response = session.get(f"{API_BASE}/datasets")
    if response.status_code == 200:
        return response.json()['results']
    return []

def get_data_fields(dataset_id, limit=500):
    params = {
        "dataset.id": dataset_id,
        "limit": limit,
        "offset": 0
    }
    response = session.get(f"{API_BASE}/data-fields", params=params)
    if response.status_code == 200:
        return response.json()['results']
    return []

datasets = get_datasets(limit=100)
unique_datasets = {d['id']: d['name'] for d in datasets}

print(f"Extracting fields for {len(unique_datasets)} datasets...")
os.makedirs("e:/CODING/MMO/wq-brain/WQ-Brainn/research-doc", exist_ok=True)
with open("e:/CODING/MMO/wq-brain/WQ-Brainn/research-doc/data_fields_list.md", "w", encoding="utf-8") as f:
    f.write("# WorldQuant Brain Available Data Fields\n\n")
    for d_id, d_name in unique_datasets.items():
        fields = get_data_fields(d_id, limit=1000)
        f.write(f"## Dataset: {d_id} - {d_name}\n")
        if not fields:
            f.write("*No fields found or access denied*\n\n")
            continue
        for field in fields:
            f.write(f"- `{field['id']}`: {field.get('description', '')}\n")
        f.write("\n")
        print(f"Saved {len(fields)} fields for {d_id}")

print("Extraction complete. Saved to research-doc/data_fields_list.md")
