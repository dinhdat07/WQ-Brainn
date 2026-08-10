import json

def main():
    with open('E:/CODING/MMO/wq-brain/wq-alpha-research/references/wq_usa_top3000_delay1_data_fields.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    snt_fields = [d for d in data if 'sentiment' in d['id'].lower() or ('category' in d and isinstance(d['category'], dict) and d['category'].get('id') in ['sentiment', 'socialmedia'])]
    
    print(f"Found {len(snt_fields)} sentiment fields.")
    for f in snt_fields[:100]:
        cat = f.get('category', {}).get('id', '')
        print(f"[{cat}] {f['id']} - {f.get('description', '')[:50]}")

if __name__ == "__main__":
    main()
