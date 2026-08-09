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

    alphas = {}

    # 1. Term structure grid
    for d in [10, 30, 60, 90, 180]:
        skew = f"group_zscore(ts_backfill(implied_volatility_put_{d} - implied_volatility_call_{d}, 20), subindustry)"
        # Matching window
        alphas[f"P13_F_IVSkew_{d}d_MatchingWin"] = {
            "regular": f"ts_decay_linear(ts_corr((close / ts_delay(close, 1)) - 1, volume, {min(d, 60)}) * {skew}, 80)",
            "neutralization": "SUBINDUSTRY"
        }
        # Fixed 20d window
        alphas[f"P13_F_IVSkew_{d}d_20dWin"] = {
            "regular": f"ts_decay_linear(ts_corr((close / ts_delay(close, 1)) - 1, volume, 20) * {skew}, 80)",
            "neutralization": "SUBINDUSTRY"
        }

    # 2. Alternative Volume metrics with 20d IV Skew
    skew20 = "group_zscore(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), subindustry)"
    alphas["P13_F_IVSkew20_VWAPCorr"] = {
        "regular": f"ts_decay_linear(ts_corr((close / ts_delay(close, 1)) - 1, vwap, 20) * {skew20}, 80)",
        "neutralization": "SUBINDUSTRY"
    }
    alphas["P13_F_IVSkew20_TurnoverCorr"] = {
        "regular": f"ts_decay_linear(ts_corr((close / ts_delay(close, 1)) - 1, volume / sharesout, 20) * {skew20}, 80)",
        "neutralization": "SUBINDUSTRY"
    }

    results = {}
    out_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase13/phase13_batch_16_results.json'

    if os.path.exists(out_file):
        with open(out_file, 'r') as f:
            results = json.load(f)

    for name, config in alphas.items():
        if name in results: continue
        formula = config["regular"]
        neut = config["neutralization"]
        print(f"Simulating {name}...")
        
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

    print("\nBatch 16 submission complete.")

if __name__ == "__main__":
    main()
