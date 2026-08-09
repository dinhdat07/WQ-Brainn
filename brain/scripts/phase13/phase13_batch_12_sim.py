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
        "Phase13_F34_Yield_ShortInt_Pos": {
            "regular": "ts_decay_linear(group_zscore(ts_backfill(anl4_fs_detail_estimates_basic_af_v4_nd_eps_mean, 5) / close, subindustry) + group_zscore(ts_backfill(news_short_interest, 20), subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F34_Yield_ShortInt_Neg": {
            "regular": "-(ts_decay_linear(group_zscore(ts_backfill(anl4_fs_detail_estimates_basic_af_v4_nd_eps_mean, 5) / close, subindustry) + group_zscore(ts_backfill(news_short_interest, 20), subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F35_Yield_PCR_Pos": {
            "regular": "ts_decay_linear(group_zscore(ts_backfill(anl4_fs_detail_estimates_basic_af_v4_nd_eps_mean, 5) / close, subindustry) - group_zscore(ts_backfill(pcr_vol_10, 5), subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F35_Yield_PCR_Neg": {
            "regular": "-(ts_decay_linear(group_zscore(ts_backfill(anl4_fs_detail_estimates_basic_af_v4_nd_eps_mean, 5) / close, subindustry) - group_zscore(ts_backfill(pcr_vol_10, 5), subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F36_FScoreGrowth": {
            "regular": "ts_decay_linear(group_zscore(fscore_growth, subindustry), 20)",
            "neutralization": "SUBINDUSTRY"
        },
        "Phase13_F36_FScoreGrowth_Neg": {
            "regular": "-(ts_decay_linear(group_zscore(fscore_growth, subindustry), 20))",
            "neutralization": "SUBINDUSTRY"
        }
    }

    results = {}
    out_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase13/phase13_batch_12_results.json'

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

    print("\nBatch 12 submission complete.")

if __name__ == "__main__":
    main()
