import os
import sys
import time
import pandas as pd
import numpy as np

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

SUBMITTED_ALPHAS = [
    "88pomANl", "6Xpn9V2L", "Jjv1g3xO", "d5RaEvVj", 
    "bldOZEjr", "RR1bxvea", "e7x3P7gO", "le3WZmdl", "ZYKo6R78"
]

def fetch_pnl_series(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    for _ in range(3):
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                records = data.get("records", [])
                if records:
                    df = pd.DataFrame(records, columns=["date", "pnl"])
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.sort_values("date").set_index("date")
                    return df["pnl"]
        except Exception as e:
            pass
        time.sleep(1)
    return None

def check_candidate_vs_portfolio(candidate_id):
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    print(f"\n================ CHECKING CANDIDATE: {candidate_id} ================")
    cand_s = fetch_pnl_series(session, candidate_id)
    if cand_s is None:
        print(f"Failed to fetch PnL for candidate {candidate_id}")
        return
        
    pnl_dict = {candidate_id: cand_s}
    for sub_id in SUBMITTED_ALPHAS:
        s = fetch_pnl_series(session, sub_id)
        if s is not None:
            pnl_dict[sub_id] = s
        else:
            print(f"Warning: Could not load PnL for submitted alpha {sub_id}")
            
    df_pnl = pd.DataFrame(pnl_dict).dropna()
    
    # 1. Check cumulative PnL correlation
    pnl_corr = df_pnl.corr()[candidate_id]
    
    # 2. Check daily returns correlation
    df_ret = df_pnl.diff().dropna()
    ret_corr = df_ret.corr()[candidate_id]
    
    print(f"\nResults against {len(SUBMITTED_ALPHAS)} Submitted Alphas:")
    print(f"{'Submitted ID':<12} | {'PnL Corr':<10} | {'Daily Ret Corr':<15} | {'Status'}")
    print("-" * 55)
    
    max_pnl_corr = -1.0
    worst_pnl_id = ""
    for sub_id in SUBMITTED_ALPHAS:
        if sub_id in pnl_corr:
            pc = pnl_corr[sub_id]
            rc = ret_corr[sub_id]
            status = "[FAIL (>= 0.70)]" if rc >= 0.70 else "[PASS (< 0.70)]"
            print(f"{sub_id:<12} | {pc:9.4f}  | {rc:14.4f}  | {status}")
            if pc > max_pnl_corr:
                max_pnl_corr = pc
                worst_pnl_id = sub_id
                
    print("-" * 55)
    print(f"Worst match: {worst_pnl_id} (PnL Corr: {max_pnl_corr:.4f}, Ret Corr: {ret_corr.get(worst_pnl_id, 0):.4f})")
    if ret_corr.max() < 0.70:
        print(f"SUCCESS! {candidate_id} PASSES ALL SELF-CORRELATION TESTS (< 0.70)!")
    else:
        print(f"REJECTED! {candidate_id} FAILS self-correlation constraint vs {worst_pnl_id}.")

if __name__ == "__main__":
    cid = sys.argv[1] if len(sys.argv) > 1 else "RRm3ZdRg"
    check_candidate_vs_portfolio(cid)
