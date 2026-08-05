import os
import sys
import json
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_iv_alphas():
    alphas = []
    
    alphas.append({
        "name": "Phase12_VRP_Rev60",
        "regular": "ts_decay_linear(group_zscore(-ts_delta(ts_backfill(implied_volatility_mean_60 / parkinson_volatility_60, 60), 5), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    alphas.append({
        "name": "Phase12_VRP_Rank60",
        "regular": "ts_decay_linear(group_rank(ts_backfill(implied_volatility_mean_60 / parkinson_volatility_60, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    alphas.append({
        "name": "Phase12_TermStruct_20_120",
        "regular": "ts_decay_linear(group_zscore(ts_backfill(implied_volatility_mean_20, 60) / ts_backfill(implied_volatility_mean_120, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    alphas.append({
        "name": "Phase12_TermStruct_10_60",
        "regular": "ts_decay_linear(group_zscore(ts_backfill(implied_volatility_mean_10, 60) / ts_backfill(implied_volatility_mean_60, 60), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    alphas.append({
        "name": "Phase12_Skew_Acc_60",
        "regular": "ts_decay_linear(group_zscore(-ts_delta(ts_backfill(implied_volatility_call_60 - implied_volatility_put_60, 60), 3), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    alphas.append({
        "name": "Phase12_Skew_Rev_60",
        "regular": "ts_decay_linear(group_zscore(-(ts_backfill(implied_volatility_call_60 - implied_volatility_put_60, 60)), subindustry), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)

    # Configure retries
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 500, 502, 503, 504 ])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    alphas = generate_iv_alphas()
    
    simulation_data = {
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
        "regular": ""
    }

    results = []
    
    for alpha in alphas:
        print(f"Submitting: {alpha['name']}")
        sim_payload = simulation_data.copy()
        sim_payload["regular"] = alpha["regular"]
        
        retries_local = 3
        while retries_local > 0:
            try:
                resp = session.post(brain1.SIMULATE_URL, json=sim_payload, timeout=30)
                if resp.status_code == 201:
                    progress_url = resp.headers.get("Location")
                    alpha["progress_url"] = progress_url
                    results.append(alpha)
                    print(f"-> OK, progress: {progress_url}")
                    break
                elif resp.status_code == 429: # Too Many Requests / Concurrent Limit
                    print("-> Rate limited! Waiting 30s...")
                    time.sleep(30)
                    retries_local -= 1
                else:
                    print(f"-> FAILED: {resp.text}")
                    break
            except Exception as e:
                print(f"Error submitting {alpha['name']}: {e}")
                time.sleep(10)
                retries_local -= 1
                
            # Wait a bit between retries
            time.sleep(2)
        
        time.sleep(2) # small delay between submits to be nice

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_01_pending.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Done submitting!")

if __name__ == "__main__":
    main()
