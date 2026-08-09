import os
import sys
import time
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)
    
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    F1_base = "ts_rank(ts_backfill(vec_avg(shares_sold_short), 20), 20) * ((close - open) / ((high - low) + 0.001))"
    F4_Skew = "implied_volatility_call_30 - implied_volatility_put_30"
    F5_Skew = "implied_volatility_mean_skew_30"
    
    alphas = {
        "Phase13_F4_IV_Skew_Pos": {
            "regular": f"ts_decay_linear(group_zscore(ts_backfill({F4_Skew}, 5), subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F4_IV_Skew_Neg": {
            "regular": f"-(ts_decay_linear(group_zscore(ts_backfill({F4_Skew}, 5), subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F5_IV_MeanSkew_Pos": {
            "regular": f"ts_decay_linear(group_zscore(ts_backfill({F5_Skew}, 5), subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F5_IV_MeanSkew_Neg": {
            "regular": f"-(ts_decay_linear(group_zscore(ts_backfill({F5_Skew}, 5), subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F1_W1": {
            "regular": f"-ts_decay_linear(group_zscore({F1_base}, subindustry), 80)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F1_W2": {
            "regular": f"-group_zscore(ts_decay_linear({F1_base}, 80), subindustry)",
            "neutralization": "SUBINDUSTRY"
        }
    }

    results = {}

    for name, config in alphas.items():
        formula = config["regular"]
        neut = config["neutralization"]
        print(f"Simulating {name} with {neut} neutralization...")
        
        payload = {
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "USA",
                "universe": "TOP3000",
                "delay": 1,
                "decay": 0,
                "neutralization": neut,
                "truncation": 0.08,
                "pasteurization": "ON",
                "unitHandling": "VERIFY",
                "nanHandling": "OFF",
                "language": "FASTEXPR",
                "visualization": False,
            },
            "regular": formula
        }

        try:
            resp = session.post(brain1.SIMULATE_URL, json=payload, timeout=30)
            
            if resp.status_code == 201:
                location = resp.headers.get("Location")
                sim_id = location.split("/")[-1] if location else "UNKNOWN"
                print(f"  -> Success! Sim ID: {sim_id}")
                results[name] = {"id": sim_id, "status": "simulating"}
            else:
                print(f"  -> Error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"  -> Exception: {e}")
            
        time.sleep(12) 

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase13/phase13_batch_05_results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\nBatch 05 submission complete. Results saved to phase13_batch_05_results.json")

if __name__ == "__main__":
    main()
