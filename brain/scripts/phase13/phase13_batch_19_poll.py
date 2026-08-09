import sys
import json
import time
import requests
import numpy as np
import pandas as pd

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

SUBMITTED_ALPHAS = [
    "2rpzj59P", "3qpd8ee6", "6Xpn9V2L", "78z9d2d5", "88pomANl",
    "bldOZEjr", "d5RaEvVj", "e7x3P7gO", "Jjv1g3xO", "le3WZmdl",
    "RR1bxvea", "ZYKo6R78"
]

def fetch_daily_pnl(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    for _ in range(5):
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200 and resp.text.strip():
                data = resp.json()
                records = data.get("records", [])
                if not records:
                    return None
                dates, pnls = [], []
                for r in records:
                    if isinstance(r, list) and len(r) >= 2:
                        dates.append(r[0])
                        pnls.append(r[1])
                    elif isinstance(r, dict):
                        dates.append(r.get("date"))
                        pnls.append(r.get("pnl"))
                df = pd.DataFrame({"date": dates, "pnl": pnls}).dropna()
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date").set_index("date")
                daily = df["pnl"].diff().dropna()
                return daily
        except Exception:
            pass
        time.sleep(1)
    return None

def check_correlation(session, target_alpha_id):
    target_daily = fetch_daily_pnl(session, target_alpha_id)
    if target_daily is None:
        return 999.0, "Failed to load PnL"
    max_p = -1.0
    worst = ""
    for sub_id in SUBMITTED_ALPHAS:
        sub_daily = fetch_daily_pnl(session, sub_id)
        if sub_daily is not None:
            common = pd.concat([target_daily, sub_daily], axis=1, join="inner").dropna()
            if len(common) > 20:
                p_corr = abs(np.corrcoef(common.iloc[:, 0], common.iloc[:, 1])[0, 1])
                if p_corr > max_p:
                    max_p = p_corr
                    worst = sub_id
    return max_p, worst

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    res_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_19_results.json"
    with open(res_file, "r") as f:
        alphas = json.load(f)
        
    pending = [n for n, d in alphas.items() if d.get("status") == "simulating"]
    print(f"Polling {len(pending)} pending simulations for Batch 19...")
    
    while pending:
        for n in pending[:]:
            sim_id = alphas[n].get("id")
            if not sim_id:
                pending.remove(n)
                continue
            try:
                resp = session.get(f"https://api.worldquantbrain.com/simulations/{sim_id}")
                if resp.status_code == 200:
                    st = resp.json().get("status")
                    if st == "ERROR":
                        err = resp.json().get("message", "unknown error")
                        print(f"[{n}] ERROR: {err}")
                        alphas[n]["status"] = "ERROR"
                        alphas[n]["error"] = err
                        pending.remove(n)
                    elif st == "COMPLETE":
                        alpha_id = resp.json().get("alpha")
                        alphas[n]["status"] = "COMPLETE"
                        alphas[n]["alpha_id"] = alpha_id
                        print(f"[{n}] COMPLETE! Alpha ID: {alpha_id}")
                        pending.remove(n)
            except Exception as e:
                print(f"[{n}] Polling exception: {e}")
        time.sleep(10)
        with open(res_file, "w") as f:
            json.dump(alphas, f, indent=4)
            
    print("\n=== FETCHING METRICS & RUNNING CORRELATION AUDITS ===")
    for n, d in alphas.items():
        if d.get("status") == "COMPLETE":
            alpha_id = d.get("alpha_id")
            try:
                resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
                if resp.status_code == 200:
                    m = resp.json().get("is", {})
                    d["metrics"] = m
                    sharpe = m.get("sharpe", 0)
                    fitness = m.get("fitness", 0)
                    turnover = m.get("turnover", 0)
                    ret = m.get("returns", 0)
                    sub_sharpe = m.get("subuniverseSharpe", 0)
                    print(f"\n[{n}] Alpha ID: {alpha_id}")
                    print(f"  Sharpe: {sharpe} | Fit: {fitness} | TO: {turnover*100:.1f}% | Ret: {ret*100:.1f}% | SubSh: {sub_sharpe}")
                    
                    if sharpe > 1.2 or fitness > 1.0:
                        max_c, worst_sub = check_correlation(session, alpha_id)
                        d["max_correlation"] = max_c
                        d["worst_correlation_alpha"] = worst_sub
                        print(f"  --> Max Corr vs Active Portfolio: {max_c:.4f} (vs {worst_sub})")
            except Exception as e:
                print(f"[{n}] Error fetching metrics: {e}")
                
    with open(res_file, "w") as f:
        json.dump(alphas, f, indent=4)
    print("\nBatch 19 evaluation complete.")

if __name__ == "__main__":
    main()
