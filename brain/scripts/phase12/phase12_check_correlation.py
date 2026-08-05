import os
import sys
import json
import time
import requests
import pandas as pd

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def get_pnl_series(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    retries = 3
    while retries > 0:
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                records = data.get("records", [])
                if not records:
                    return None
                df = pd.DataFrame(records, columns=["date", "pnl"])
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date").set_index("date")
                return df["pnl"]
            elif resp.status_code == 429:
                print(f"[{alpha_id}] Rate limited, waiting 30s...")
                time.sleep(30)
                retries -= 1
            else:
                print(f"[{alpha_id}] Error {resp.status_code}: {resp.text[:100]}")
                return None
        except Exception as e:
            print(f"[{alpha_id}] Exception: {e}")
            retries -= 1
            time.sleep(5)
    return None


def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)

    results_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_01_results.json'
    
    if not os.path.exists(results_file):
        print(f"Results file not found: {results_file}")
        # The script phase12_poll didn't dump results json! I should just check the specific one manually.
        pass

    # We know Phase12_VRP_Rank60 | ID: MPGwZK7a | Sharpe: 1.22
    candidates = {
        "Phase12_VRP_Rank60": "MPGwZK7a",
        "Phase11_V1": "78z9d2d5",
        "Phase10_V2": "d5RaEvVj",
        "Phase9": "88pomANl"
    }

    print(f"Fetching PnL for {list(candidates.keys())}...")
    pnl_dict = {}
    for name, aid in candidates.items():
        s = get_pnl_series(session, aid)
        if s is not None:
            pnl_dict[name] = s
        time.sleep(2)
            
    df_pnl = pd.DataFrame(pnl_dict).dropna()
    print("\n================ Pairwise PnL Correlation Matrix ================")
    corr_matrix = df_pnl.corr()
    print(corr_matrix.round(4))

if __name__ == "__main__":
    main()
