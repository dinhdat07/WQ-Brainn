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

    ret = "((close / ts_delay(close, 1)) - 1)"
    
    # VRP Expressions
    vrp_call = "group_zscore(ts_backfill(implied_volatility_call_20 - historical_volatility_20, 20), subindustry)"
    vrp_put = "group_zscore(ts_backfill(implied_volatility_put_20 - historical_volatility_20, 20), subindustry)"
    vrp_total = "group_zscore(ts_backfill(implied_volatility_call_20 + implied_volatility_put_20 - 2 * historical_volatility_20, 20), subindustry)"

    alphas = {
        # 1. Multiplied by PV Correlation
        "P13_F49_VRP_Call_PVCorr_Pos": {
            "regular": f"ts_decay_linear(ts_corr({ret}, volume, 20) * {vrp_call}, 80)",
            "neutralization": "SUBINDUSTRY"
        },
        "P13_F49_VRP_Call_PVCorr_Neg": {
            "regular": f"-(ts_decay_linear(ts_corr({ret}, volume, 20) * {vrp_call}, 80))",
            "neutralization": "SUBINDUSTRY"
        },
        "P13_F50_VRP_Put_PVCorr_Pos": {
            "regular": f"ts_decay_linear(ts_corr({ret}, volume, 20) * {vrp_put}, 80)",
            "neutralization": "SUBINDUSTRY"
        },
        "P13_F50_VRP_Put_PVCorr_Neg": {
            "regular": f"-(ts_decay_linear(ts_corr({ret}, volume, 20) * {vrp_put}, 80))",
            "neutralization": "SUBINDUSTRY"
        },
        "P13_F51_VRP_Total_PVCorr_Pos": {
            "regular": f"ts_decay_linear(ts_corr({ret}, volume, 20) * {vrp_total}, 80)",
            "neutralization": "SUBINDUSTRY"
        },
        "P13_F51_VRP_Total_PVCorr_Neg": {
            "regular": f"-(ts_decay_linear(ts_corr({ret}, volume, 20) * {vrp_total}, 80))",
            "neutralization": "SUBINDUSTRY"
        },
        # 2. Pure Directional VRP with fast decay
        "P13_F52_Pure_VRP_Call_Rev": {
            "regular": f"-ts_decay_linear({vrp_call}, 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "P13_F53_Pure_VRP_Put_Rev": {
            "regular": f"-ts_decay_linear({vrp_put}, 20)",
            "neutralization": "SUBINDUSTRY"
        }
    }

    results = {}
    out_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase13/phase13_batch_17_results.json'

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

    print("\nBatch 17 submission complete.")

if __name__ == "__main__":
    main()
