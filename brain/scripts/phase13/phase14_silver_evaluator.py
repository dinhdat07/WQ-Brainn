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
    if resp.status_code != 200 or not resp.text.strip():
        return {}
    try:
        data = resp.json()
    except Exception:
        return {}
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
        # Silver 1: Implied Volatility Spread
        {
            "name": "Silver_1_IV_Spread",
            "expr": "trade_when(ts_backfill(pcr_oi_270, 20) < 1, (ts_backfill(implied_volatility_call_270, 20) - ts_backfill(implied_volatility_put_270, 20)), -1)",
            "decay": 4, "neut": "MARKET"
        },
        # Silver 2: 6-Month Call-Put Volatility Skew
        {
            "name": "Silver_2_Call_Put_Skew_180",
            "expr": "ts_decay_linear(group_rank((ts_backfill(implied_volatility_call_180, 20) - ts_backfill(implied_volatility_put_180, 20)) / (ts_backfill(implied_volatility_mean_180, 20) + 0.001), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # Silver 3: 5-Day Peer vs Stock Performance Gap
        {
            "name": "Silver_3_Peer_5D_Gap",
            "expr": "cum_rel = (1 + ts_delay(rel_ret_all, 4)) * (1 + ts_delay(rel_ret_all, 3)) * (1 + ts_delay(rel_ret_all, 2)) * (1 + ts_delay(rel_ret_all, 1)) * (1 + rel_ret_all); cum_ret = (1 + ts_delay(returns, 4)) * (1 + ts_delay(returns, 3)) * (1 + ts_delay(returns, 2)) * (1 + ts_delay(returns, 1)) * (1 + returns); ts_decay_linear(group_rank(cum_rel - cum_ret, sector), 5)",
            "decay": 0, "neut": "SECTOR"
        },
        # Silver 4: Investing for the Future (Long-term investment trend)
        {
            "name": "Silver_4_Long_Term_Investment_Trend",
            "expr": "ts_decay_linear(group_rank(ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        # Silver 5: Free Cash Flow Quality vs Capex Signal
        {
            "name": "Silver_5_FCF_Quality_Capex",
            "expr": "ts_decay_linear(ts_scale(ts_backfill(est_cashflow_op, 60), 252), 22) - ts_decay_linear(ts_scale(ts_backfill(est_capex, 60), 252), 22)",
            "decay": 2, "neut": "INDUSTRY"
        },
        # Silver 6: Bull Trap First-Minute News Reaction
        {
            "name": "Silver_6_Bull_Trap_News_Reaction",
            "expr": "slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 5, rettype = 2); winsorize(-ts_backfill(news_max_up_ret, 60) * abs(slope), std = 4)",
            "decay": 0, "neut": "INDUSTRY"
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
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase14_silver_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll Silver model tests completed! Saved results to {out_file}")

if __name__ == "__main__":
    main()
