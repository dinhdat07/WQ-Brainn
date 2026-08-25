import os
import json
import time
import requests

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)
    username, password = creds[0], creds[1]

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(username, password)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
session.post(f"{API_BASE}/authentication")

def simulate(expression):
    data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": expression
    }
    
    while True:
        try:
            response = session.post(f"{API_BASE}/simulations", json=data, timeout=10)
            if response.status_code == 201:
                return response.headers.get("Location").split("/")[-1]
            elif response.status_code == 429:
                print(f"429 Limit reached for {expression[:30]}, waiting 30s...")
                time.sleep(30)
            elif response.status_code == 401:
                session.post(f"{API_BASE}/authentication")
            else:
                return f"Error: {response.status_code} {response.text}"
        except Exception as e:
            return str(e)

exprs = [
    "ts_decay_linear(group_rank(anl4_fs_detail_rec_v4_nd_estimate, subindustry), 10)",
    "ts_decay_linear(group_rank(-anl4_fs_detail_rec_v4_nd_estimate, subindustry), 10)",
    "ts_decay_linear(-group_zscore(scl12_buzz - ts_mean(scl12_buzz, 10), market), 5)",
    "ts_decay_linear(group_rank(pcr_oi_all, subindustry), 10)",
    "ts_decay_linear(group_rank(-unsystematic_risk_last_30_days, sector), 10)",
    "ts_decay_linear(group_rank(fscore_bfl_quality, subindustry), 10)",
    "ts_decay_linear(group_rank(composite_factor_score_derivative, subindustry), 10)"
]

for expr in exprs:
    sim_id = simulate(expr)
    print(f"Spawned: {sim_id}")
    time.sleep(2)
