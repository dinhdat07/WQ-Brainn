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

    alphas = {
        "Phase12_IV_Skew_Div_MKT": {
            "regular": "ts_decay_linear(group_rank(ts_zscore(ts_backfill(implied_volatility_call_20, 20) - ts_backfill(implied_volatility_put_20, 20), 20) * -ts_delta(close, 5) / close, sector), 10)",
            "neutralization": "MARKET"
        },
        "Phase12_IV_Term_Ret_MKT": {
            "regular": "ts_decay_linear(group_rank(ts_zscore(ts_backfill(implied_volatility_mean_60, 60) - ts_backfill(implied_volatility_mean_20, 20), 20) * ts_sum(returns, 5), industry), 10)",
            "neutralization": "MARKET"
        },
        "Phase12_IV_Ret_Corr_MKT": {
            "regular": "ts_decay_linear(group_rank(-ts_corr(returns, ts_backfill(implied_volatility_mean_20, 20), 10), subindustry), 5)",
            "neutralization": "MARKET"
        },
        "Phase12_VRP_Intraday_MKT": {
            "regular": "ts_decay_linear(group_rank(ts_zscore(ts_backfill(implied_volatility_mean_60, 60) / parkinson_volatility_60, 60) * -(close/open - 1), subindustry), 10)",
            "neutralization": "MARKET"
        },
        "Phase12_IV_Rank_MKT": {
            "regular": "-ts_decay_linear(group_rank(ts_rank(ts_backfill(implied_volatility_mean_20, 20), 252), sector), 10)",
            "neutralization": "MARKET"
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
            
        time.sleep(3) 

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_03_results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\nBatch 03 submission complete. Results saved to phase12_batch_03_results.json")

if __name__ == "__main__":
    main()
