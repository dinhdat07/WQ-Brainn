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
        
    print(f"\nReady to test FRESH ORTHOGONAL ALPHA IDEAS!")
    
    # Define fresh ideas
    candidates = [
        # Domain 1: Idiosyncratic Risk (Ang et al. Low Volatility Anomaly)
        {
            "name": "Idiosyncratic_Risk_Rank_Decay",
            "expr": "-group_rank(unsystematic_risk_last_90_days, subindustry)",
            "decay": 15, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Idiosyncratic_Risk_Momentum_Hybrid",
            "expr": "-group_rank(unsystematic_risk_last_90_days, subindustry) + group_rank(ts_delta(close, 252) / ts_lag(close, 252), subindustry)",
            "decay": 10, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Idiosyncratic_Risk_Decay_Linear",
            "expr": "ts_decay_linear(-group_rank(unsystematic_risk_last_90_days, subindustry), 20)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 2: News Sentiment & Narrative Impact (RavenPack NLP)
        {
            "name": "News_Sentiment_Polarity_Decay",
            "expr": "ts_decay_linear(group_rank(ts_backfill(nws18_qep, 20), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "News_Granular_Sentiment_Acceleration",
            "expr": "ts_decay_linear(group_rank(ts_backfill(nws18_ssc, 20) - ts_mean(ts_backfill(nws18_ssc, 20), 60), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "News_Narrative_Impact_Flow",
            "expr": "ts_decay_linear(group_rank(ts_backfill(nws18_nip, 20), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 3: Social Buzz & Attention Mean Reversion
        {
            "name": "Social_Buzz_Overheating_Reversal",
            "expr": "ts_decay_linear(-group_rank(ts_backfill(scl12_buzz, 20) / (ts_mean(ts_backfill(scl12_buzz, 20), 60) + 0.01), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Social_Sentiment_ZScore_Momentum",
            "expr": "ts_decay_linear(group_rank(ts_backfill(snt_social_value, 20), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 4: Parkinson Volatility Ratio (Intraday Jump vs Close-to-Close Dislocation)
        {
            "name": "Parkinson_Realized_Jump_Ratio",
            "expr": "ts_decay_linear(group_rank(parkinson_volatility_10 / historical_volatility_10, subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Options_PCR_Volume_Contrarian",
            "expr": "ts_decay_linear(group_rank(1 / (ts_backfill(pcr_vol_270, 30) + 0.01), subindustry), 10)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        
        # Domain 5: Share Turnover Velocity Anomaly (Datar, Naik, Radcliffe 1998)
        {
            "name": "Share_Turnover_Velocity_Anomaly",
            "expr": "ts_decay_linear(-group_rank(adv20 / (sharesout * close + 1), subindustry), 20)",
            "decay": 0, "neut": "SUBINDUSTRY"
        },
        {
            "name": "Amihud_Illiquidity_Factor",
            "expr": "ts_decay_linear(group_rank(ts_mean(abs(returns) / (volume * close + 1), 60), subindustry), 20)",
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
            print(f"❌ Simulation request failed: {resp.status_code} {resp.text}")
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
                    print(f"❌ Sim status: {s_status} -> {s_data.get('message')}")
                    break
            else:
                print(f"Error polling: {s_resp.status_code}")
                
        if not alpha_id:
            print("Skipping due to simulation incomplete.")
            continue
            
        # Get alpha details
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
        
        # Calculate max correlation with active portfolio
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
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase14_fresh_domains_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll tests completed! Saved results to {out_file}")

if __name__ == "__main__":
    main()
