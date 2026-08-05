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
    
    # Configure retry logic for 429 errors
    retry_strategy = Retry(
        total=5,
        backoff_factor=2, # 2, 4, 8, 16, 32
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    alphas = {
        # 1. Exact same formula as MPGwZK7a (Sharpe 1.22), but MARKET neutralization
        "Phase12_VRP_Rank60_MARKET": {
            "regular": "ts_decay_linear(group_rank(ts_backfill(implied_volatility_mean_60 / parkinson_volatility_60, 60), subindustry), 10)",
            "neutralization": "MARKET"
        },
        # 2. Exact same formula, but SECTOR neutralization
        "Phase12_VRP_Rank60_SECTOR": {
            "regular": "ts_decay_linear(group_rank(ts_backfill(implied_volatility_mean_60 / parkinson_volatility_60, 60), subindustry), 10)",
            "neutralization": "SECTOR"
        },
        # 3. New Skew divergence (call - put) IV.
        "Phase12_IV_Skew_Div_MKT": {
            "regular": "ts_decay_linear(group_rank( ts_backfill(implied_volatility_call_20 - implied_volatility_put_20, 20) * (ts_max(high, 5) - close) / close , sector), 5)",
            "neutralization": "MARKET"
        },
        # 4. IV Term Structure interaction with Returns
        "Phase12_IV_Term_Ret_MKT": {
            "regular": "ts_ewma(group_rank( ts_backfill(implied_volatility_mean_60 - implied_volatility_mean_20, 20) / ts_backfill(implied_volatility_mean_20, 20) * sum(returns, 5), sector), 5)",
            "neutralization": "MARKET"
        },
        # 5. Correlation between IV and Price 
        "Phase12_IV_Ret_Corr_MKT": {
            "regular": "ts_decay_linear(group_rank(correlation(returns, ts_backfill(implied_volatility_mean_20, 20), 10), sector), 5)",
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
                alpha_id = location.split("/")[-1] if location else "UNKNOWN"
                print(f"  -> Success! Alpha ID: {alpha_id}")
                results[name] = {"id": alpha_id, "status": "simulating"}
            else:
                print(f"  -> Error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"  -> Exception: {e}")
            
        time.sleep(5) # avoid aggressive polling

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_02_results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\nBatch 02 submission complete. Results saved to phase12_batch_02_results.json")

if __name__ == "__main__":
    main()
