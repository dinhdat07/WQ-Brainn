import os
import sys
import json
import time
import requests
import numpy as np

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def get_daily_pnl_returns(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    resp = session.get(url)
    if resp.status_code != 200:
        return {}
    data = resp.json()
    records = sorted(data.get("records", []), key=lambda r: r[0])
    daily_diffs = {}
    for i in range(1, len(records)):
        dt = records[i][0]
        daily_diffs[dt] = float(records[i][1]) - float(records[i-1][1])
    return daily_diffs

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    # 1. Fetch active alphas
    resp = session.get("https://api.worldquantbrain.com/users/self/alphas?stage=OS&limit=50")
    active_alphas = resp.json().get("results", [])
    print(f"Loaded {len(active_alphas)} active OS alphas. Pre-fetching daily returns...")
    
    active_rets = {}
    for a in active_alphas:
        aid = a["id"]
        r = get_daily_pnl_returns(session, aid)
        if len(r) > 100:
            active_rets[aid] = r
            print(f"  - Active [{aid}] loaded: {len(r)} days")
        time.sleep(0.2)
        
    candidates = [
        # Set A: Pure Style Surface Derivatives (No price returns in formula!)
        {
            "name": "Multi_Factor_Acceleration_Pure",
            "expr": "ts_decay_linear(group_rank(multi_factor_acceleration_score_derivative, subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Cashflow_Efficiency_vs_Valuation_Derivative",
            "expr": "ts_decay_linear(group_rank(cashflow_efficiency_rank_derivative, subindustry) - group_rank(relative_valuation_rank_derivative, subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Growth_Potential_Derivative_Pure",
            "expr": "ts_decay_linear(group_rank(growth_potential_rank_derivative, subindustry), 20)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Set B: Pure Customer / Supplier Network Momentum (No price returns subtraction!)
        {
            "name": "Customer_Network_LeadLag_Pure",
            "expr": "ts_decay_linear(group_rank(ts_mean(ts_backfill(rel_ret_cust, 15), 10), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Partner_Network_LeadLag_Pure",
            "expr": "ts_decay_linear(group_rank(ts_mean(ts_backfill(rel_ret_part, 15), 10), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Set C: Pure Options Implied Vol Skew & Put-Call Sentiment
        {
            "name": "Option_IV_Call_Put_Skew",
            "expr": "ts_decay_linear(group_rank(ts_backfill(implied_volatility_call_30, 10) / (ts_backfill(implied_volatility_put_30, 10) + 0.001), subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Option_PCR_Volume_Sentiment",
            "expr": "ts_decay_linear(-group_rank(ts_mean(ts_backfill(pcr_vol_270, 15), 5), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Set D: Operating Cashflow Quality Spread (Silver #5)
        {
            "name": "Operating_Cashflow_vs_Capex_Quality",
            "expr": "ts_decay_linear(group_rank(ts_backfill(est_cashflow_op, 60) / cap, subindustry) - group_rank(ts_backfill(est_capex, 60) / cap, subindustry), 20)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Set E: Long-Term Asset Growth / Capital Investment (Silver #4)
        {
            "name": "Long_Term_Capital_Investment_Quality",
            "expr": "ts_decay_linear(-group_rank(ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2), subindustry), 20)",
            "decay": 0, "neut": "SUBINDUSTRY"
        }
    ]
    
    results = []
    for cand in candidates:
        print(f"\n=======================================================")
        print(f"Testing Candidate: {cand['name']}")
        print(f"Formula: {cand['expr']}")
        print(f"Decay: {cand['decay']}, Neut: {cand['neut']}")
        
        payload = {
            "type": "REGULAR",
            "settings": {
                "instrumentType": "EQUITY",
                "region": "USA",
                "universe": "TOP3000",
                "delay": 1,
                "decay": cand["decay"],
                "neutralization": cand["neut"],
                "truncation": 0.08,
                "pasteurization": "ON",
                "unitHandling": "VERIFY",
                "nanHandling": "ON",
                "language": "FASTEXPR",
                "visualization": False,
            },
            "regular": cand["expr"],
        }
        
        resp = session.post("https://api.worldquantbrain.com/simulations", json=payload)
        if resp.status_code != 201:
            print(f"Simulation request failed: {resp.status_code} {resp.text}")
            time.sleep(3)
            continue
            
        sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
        print(f"Sim ID: {sim_id}. Polling...")
        
        alpha_id = None
        for _ in range(40):
            time.sleep(5)
            s_resp = session.get(f"https://api.worldquantbrain.com/simulations/{sim_id}")
            if s_resp.status_code == 200:
                s_data = s_resp.json()
                s_status = s_data.get("status")
                if s_status == "COMPLETE":
                    alpha_id = s_data.get("alpha")
                    break
                elif s_status in ["ERROR", "FAIL", "CANCELLED"]:
                    print(f"Sim status: {s_status} -> {s_data.get('message')}")
                    break
            else:
                print(f"Error polling: {s_resp.status_code}")
                
        if not alpha_id:
            print("Skipping due to simulation incomplete.")
            time.sleep(2)
            continue
            
        a_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
        if a_resp.status_code != 200:
            print("Failed to get alpha details")
            continue
            
        a_data = a_resp.json()
        is_data = a_data.get("is", {})
        sharpe = is_data.get("sharpe", 0)
        fitness = is_data.get("fitness", 0)
        turnover = is_data.get("turnover", 0)
        margin = is_data.get("margin", 0)
        sub_sharpe = is_data.get("subUniverseSharpe", 0)
        checks = is_data.get("checks", [])
        
        print(f"\n[METRICS] [{alpha_id}] Sharpe: {sharpe:.2f} | Fitness: {fitness:.2f} | TO: {turnover*100:.1f}% | SubSharpe: {sub_sharpe:.2f}")
        
        new_ret = get_daily_pnl_returns(session, alpha_id)
        
        max_corr = 0.0
        max_corr_id = None
        corrs = {}
        
        if len(new_ret) > 100:
            for old_id, old_ret in active_rets.items():
                common_dates = sorted(set(new_ret.keys()).intersection(set(old_ret.keys())))
                if len(common_dates) > 100:
                    v1 = [new_ret[d] for d in common_dates]
                    v2 = [old_ret[d] for d in common_dates]
                    c = float(np.corrcoef(v1, v2)[0, 1])
                    corrs[old_id] = round(c, 4)
                    if abs(c) > abs(max_corr):
                        max_corr = c
                        max_corr_id = old_id
                        
        print(f"[CORRELATION] Max Daily Correlation with Active 13 Alphas: {max_corr:.4f} (vs {max_corr_id})")
        print(f"   Correlations breakdown: {corrs}")
        
        results.append({
            "name": cand["name"],
            "alpha_id": alpha_id,
            "formula": cand["expr"],
            "sharpe": sharpe,
            "fitness": fitness,
            "turnover": turnover,
            "margin": margin,
            "sub_sharpe": sub_sharpe,
            "max_corr": max_corr,
            "max_corr_id": max_corr_id,
            "corrs": corrs,
            "checks": checks
        })
        time.sleep(2)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase14_pure_orthogonal_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll pure orthogonal tests completed! Saved results to {out_file}")

if __name__ == "__main__":
    main()
