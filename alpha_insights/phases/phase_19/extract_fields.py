import json
import requests
import os

API_BASE = 'https://api.worldquantbrain.com'
with open('e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt') as f:
    creds = json.load(f)
session = requests.Session()
session.auth = (creds[0], creds[1])
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f'{API_BASE}/authentication')

keywords = ["short", "supply", "option", "implied", "volatility", "news", "sentiment", "buzz", "model", "machine", "analyst", "target"]
all_fields = {}

for kw in keywords:
    print(f"Searching for '{kw}'...")
    limit = 50
    offset = 0
    while True:
        r = session.get(f'{API_BASE}/data-fields', params={
            'instrumentType': 'EQUITY', 
            'region': 'USA', 
            'delay': 1, 
            'universe': 'TOP3000', 
            'search': kw,
            'limit': limit,
            'offset': offset
        })
        data = r.json()
        if isinstance(data, list):
            break
        
        batch = data.get("results", [])
        if not batch:
            break
        
        for field in batch:
            all_fields[field['id']] = field
            
        if len(batch) < limit:
            break
        offset += limit
        # Prevent going beyond offset 500 to avoid long runs
        if offset > 500:
            break

os.makedirs('e:/CODING/MMO/wq-brain/WQ-Brainn/research-doc', exist_ok=True)

with open('e:/CODING/MMO/wq-brain/WQ-Brainn/research-doc/wq_data_fields.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_fields.values()), f, indent=2)

summary = {}
for fid, field in all_fields.items():
    cat = field.get('category', {}).get('name', 'Unknown')
    subcat = field.get('subcategory', {}).get('name', 'Unknown')
    dataset = field.get('dataset', {}).get('name', 'Unknown')
    
    if cat not in summary:
        summary[cat] = {}
    if dataset not in summary[cat]:
        summary[cat][dataset] = []
        
    summary[cat][dataset].append({
        'id': field['id'],
        'description': field.get('description', ''),
        'coverage': field.get('coverage', 0)
    })

with open('e:/CODING/MMO/wq-brain/WQ-Brainn/research-doc/wq_data_fields_summary.md', 'w', encoding='utf-8') as f:
    f.write("# WQ Brain Data Fields Summary (Extracted via Keywords)\n\n")
    for cat in sorted(summary.keys()):
        f.write(f"## Category: {cat}\n")
        for dataset in sorted(summary[cat].keys()):
            fields = sorted(summary[cat][dataset], key=lambda x: x['coverage'], reverse=True)
            f.write(f"### Dataset: {dataset} ({len(fields)} fields)\n")
            for idx, field in enumerate(fields):
                if idx < 20:
                    f.write(f"- `{field['id']}` (Coverage: {field['coverage']:.4f}): {field['description']}\n")
            if len(fields) > 20:
                f.write(f"- *... and {len(fields) - 20} more.*\n")
        f.write("\n")

print(f"Done! Extracted {len(all_fields)} unique fields.")
