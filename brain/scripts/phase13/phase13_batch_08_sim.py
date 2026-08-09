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
    print("Authenticating...")
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)
    print("Auth complete.")
    
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    alphas = {
        "Phase13_F13_PCR_Vol_10_Pos": {
            "regular": "ts_decay_linear(group_zscore(ts_backfill(pcr_vol_10, 5), subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F13_PCR_Vol_10_Neg": {
            "regular": "-(ts_decay_linear(group_zscore(ts_backfill(pcr_vol_10, 5), subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F14_PCR_Vol_Skew_Pos": {
            "regular": "ts_decay_linear(group_zscore(ts_backfill(pcr_vol_10, 5) - ts_backfill(pcr_vol_180, 5), subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F14_PCR_Vol_Skew_Neg": {
            "regular": "-(ts_decay_linear(group_zscore(ts_backfill(pcr_vol_10, 5) - ts_backfill(pcr_vol_180, 5), subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F15_IV_TermStruct_Skew_Pos": {
            "regular": "ts_decay_linear(group_zscore((ts_backfill(implied_volatility_call_30, 5) - ts_backfill(implied_volatility_call_180, 5)) - (ts_backfill(implied_volatility_put_30, 5) - ts_backfill(implied_volatility_put_180, 5)), subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F15_IV_TermStruct_Skew_Neg": {
            "regular": "-(ts_decay_linear(group_zscore((ts_backfill(implied_volatility_call_30, 5) - ts_backfill(implied_volatility_call_180, 5)) - (ts_backfill(implied_volatility_put_30, 5) - ts_backfill(implied_volatility_put_180, 5)), subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        }
    }

    results = {}
    out_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase13/phase13_batch_08_results.json'

    if os.path.exists(out_file):
        with open(out_file, 'r') as f:
            results = json.load(f)

    for name, config in alphas.items():
        if name in results: continue
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
                with open(out_file, 'w') as f: json.dump(results, f, indent=4)
            else:
                print(f"  -> Error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"  -> Exception: {e}")
            
        time.sleep(12) 

    print("\nBatch 08 submission complete.")

if __name__ == "__main__":
    main()
