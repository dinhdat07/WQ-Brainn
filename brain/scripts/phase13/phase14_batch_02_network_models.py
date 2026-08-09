import os
import sys
import json
import time
import requests
import numpy as np

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def fetch_pnl(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    resp = session.get(url)
    if resp.status_code != 200 or not resp.text.strip():
        return []
    data = resp.json()
    props = data.get("schema", {}).get("properties", [])
    if isinstance(props, list):
        date_idx = next((i for i, p in enumerate(props) if p.get("name", "").lower() == "date"), 0)
        pnl_idx = next((i for i, p in enumerate(props) if p.get("name", "").lower() in ("pnl", "cum_pnl", "returns", "ret")), 1)
    else:
        date_idx = next((v["index"] for k, v in props.items() if k.lower() == "date"), 0)
        pnl_idx = next((v["index"] for k, v in props.items() if k.lower() in ("pnl", "cum_pnl", "returns", "ret")), 1)
    records = sorted(data.get("records", []), key=lambda r: r[date_idx])
    out = []
    for row in records:
        rec = row[0] if isinstance(row, list) and len(row) == 1 and isinstance(row[0], list) else row
        try:
            out.append(float(rec[pnl_idx]))
        except Exception:
            continue
    return out

def daily_returns(cum_pnl):
    return [cum_pnl[i+1] - cum_pnl[i] for i in range(len(cum_pnl)-1)]

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    # 1. Load active alphas
    resp = session.get("https://api.worldquantbrain.com/users/self/alphas?stage=OS&limit=50")
    active_alphas = resp.json().get("results", [])
    print(f"Loaded {len(active_alphas)} active OS alphas. Pre-fetching daily returns...")
    
    active_rets = {}
    for a in active_alphas:
        aid = a["id"]
        pnl = fetch_pnl(session, aid)
        ret = daily_returns(pnl)
        if len(ret) > 100:
            active_rets[aid] = ret
            print(f"  - Active [{aid}] fetched: {len(ret)} days")
        time.sleep(0.3)
        
    print(f"\nReady to test NETWORK, STYLE-SURFACE & ECONOMIC-LINKAGE ALPHAS!")
    
    candidates = [
        # Domain 1: Product / Peer Network Lead-Lag (Silver #3)
        {
            "name": "Peer_Gap_Product_Overlap",
            "expr": "ts_decay_linear(group_rank(ts_backfill(rel_ret_all, 10) - returns, subindustry), 5)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Competitor_Network_Momentum_Spillover",
            "expr": "ts_decay_linear(group_rank(ts_mean(ts_backfill(rel_ret_comp, 10), 5) - ts_mean(returns, 5), subindustry), 5)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Supply_Chain_Partner_LeadLag",
            "expr": "ts_decay_linear(group_rank(ts_backfill(rel_ret_part, 10) - returns, subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 2: Model Style-Surface & Factor Acceleration (Novel Model Dataset)
        {
            "name": "Multi_Factor_Acceleration_Derivative",
            "expr": "ts_decay_linear(group_rank(multi_factor_acceleration_score_derivative, subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Cashflow_Efficiency_vs_Valuation_Rank",
            "expr": "ts_decay_linear(group_rank(cashflow_efficiency_rank_derivative, subindustry) - group_rank(relative_valuation_rank_derivative, subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Growth_Potential_Derivative_Alpha",
            "expr": "ts_decay_linear(group_rank(growth_potential_rank_derivative, subindustry), 15)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 3: Post-News High-Frequency Price Drift & Bull-Trap (Silver #6)
        {
            "name": "News_First_Minute_Momentum",
            "expr": "ts_decay_linear(group_rank(ts_backfill(news_pct_1min, 30), subindustry), 5)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "News_Reaction_Slope_Bull_Trap",
            "expr": "ts_decay_linear(group_rank(-ts_backfill(news_max_up_ret, 30) * abs(ts_regression(ts_backfill(news_pct_1min, 30), ts_step(1), 5, rettype = 2)), subindustry), 5)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 4: Capital Allocation & Long-Term Investment Trend (Silver #4)
        {
            "name": "Long_Term_Investment_Trend",
            "expr": "ts_decay_linear(group_rank(ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2), subindustry), 20)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 5: Operating Cashflow vs Capex Quality (Silver #5)
        {
            "name": "FCF_Quality_Spread_Signal",
            "expr": "ts_decay_linear(ts_scale(ts_backfill(est_cashflow_op, 60), 252) - ts_scale(ts_backfill(est_capex, 60), 252), 22)",
            "decay": 2, "neut": "INDUSTRY"
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
        
        print(f"\n[METRICS] [{alpha_id}] Sharpe: {sharpe:.2f} | Fitness: {fitness:.2f} | TO: {turnover*100:.1f}% | SubSharpe: {sub_sharpe:.2f}")
        
        pnl = fetch_pnl(session, alpha_id)
        new_ret = daily_returns(pnl)
        
        max_corr = 0.0
        max_corr_id = None
        corrs = {}
        
        if len(new_ret) > 100:
            for old_id, old_ret in active_rets.items():
                min_len = min(len(new_ret), len(old_ret))
                if min_len > 100:
                    c = float(np.corrcoef(new_ret[-min_len:], old_ret[-min_len:])[0, 1])
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
            "corrs": corrs
        })
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase14_network_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll tests completed! Saved results to {out_file}")

if __name__ == "__main__":
    main()
