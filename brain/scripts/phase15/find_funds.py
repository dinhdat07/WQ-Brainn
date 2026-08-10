import json

def main():
    with open('E:/CODING/MMO/wq-brain/wq-alpha-research/references/wq_usa_top3000_delay1_data_fields.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for d in data:
        desc = d.get('description', '').lower()
        id_lower = d['id'].lower()
        if 'short interest' in desc or 'eps' in desc or 'earnings per share' in desc or 'sales' in desc:
            if 'anl' in id_lower or 'est' in id_lower or 'si_' in id_lower:
                print(f"{d['id']} - {desc[:50]}")

if __name__ == "__main__":
    main()
