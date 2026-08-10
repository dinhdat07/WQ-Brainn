import sys
import json
import time
import requests
import numpy as np

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def get_daily_pnl_returns(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    for _ in range(3):
        try:
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                records = sorted(data.get("records", []), key=lambda r: r[0])
                if len(records) > 100:
                    daily_diffs = {}
                    for i in range(1, len(records)):
                        dt = records[i][0][:10]
                        daily_diffs[dt] = float(records[i][1]) - float(records[i-1][1])
                    return daily_diffs
        except Exception:
            pass
        time.sleep(2)
    return {}

def load_active_alphas(session):
    print("Loading active OS alphas...")
    url = "https://api.worldquantbrain.com/users/self/alphas?status=ACTIVE&limit=100"
    active_alphas = []
    
    while url:
        resp = session.get(url)
        if resp.status_code != 200:
            break
        data = resp.json()
        results = data.get("results", [])
        for a in results:
            if a.get("stage") == "OS":
                active_alphas.append(a)
        url = data.get("next")
        
    print(f"Total active OS alphas found: {len(active_alphas)}")
    active_rets = {}
    for a in active_alphas:
        aid = a["id"]
        r = get_daily_pnl_returns(session, aid)
        if len(r) > 100:
            active_rets[aid] = r
        time.sleep(0.5)
            
    print(f"Loaded returns for {len(active_rets)} active alphas.")
    return active_rets

def simulate_and_evaluate(session, name, code, active_rets, decay=10, neut="SUBINDUSTRY", universe="TOP3000"):
    print(f"\n=======================================================")
    print(f"[{name}] Starting Simulation...")
    print(f"Code: {code}")
    
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": universe,
            "delay": 1,
            "decay": decay,
            "neutralization": neut,
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False,
        },
        "regular": code
    }
    
    for _ in range(3):
        resp = session.post("https://api.worldquantbrain.com/simulations", json=payload)
        if resp.status_code == 201:
            break
        time.sleep(2)
        
    if resp.status_code != 201:
        print(f"[{name}] Failed to start simulation: {resp.status_code} - {resp.text}")
        return None
        
    sim_id = resp.headers["Location"].rstrip("/").split("/")[-1]
    
    alpha_id = None
    for attempt in range(60):
        time.sleep(4)
        s_resp = session.get(f"https://api.worldquantbrain.com/simulations/{sim_id}")
        if s_resp.status_code == 200:
            st = s_resp.json().get("status")
            if st == "COMPLETE":
                alpha_id = s_resp.json().get("alpha")
                break
            elif st in ["ERROR", "FAIL", "CANCELLED"]:
                print(f"[{name}] Simulation {st}: {s_resp.json().get('message')}")
                return None
                
    if not alpha_id:
        print(f"[{name}] Simulation timed out.")
        return None
        
    time.sleep(2)
    a_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
    if a_resp.status_code != 200:
        return None
        
    a_data = a_resp.json()
    is_data = a_data.get("is", {})
    sharpe = is_data.get("sharpe", 0)
    fitness = is_data.get("fitness", 0)
    turnover = is_data.get("turnover", 0)
    
    t_ret = get_daily_pnl_returns(session, alpha_id)
    max_c = 0.0
    max_id = "None"
    if len(t_ret) > 100:
        for aid, a_ret in active_rets.items():
            common = sorted(set(t_ret.keys()).intersection(set(a_ret.keys())))
            if len(common) > 100:
                v1 = [t_ret[d] for d in common]
                v2 = [a_ret[d] for d in common]
                c = float(np.corrcoef(v1, v2)[0, 1])
                if abs(c) > abs(max_c):
                    max_c = c
                    max_id = aid
                    
    print(f"[{alpha_id}] Sharpe: {sharpe:.2f} | Fitness: {fitness:.2f} | TO: {turnover*100:.1f}%")
    print(f"Max Correlation: {max_c:+.4f} (vs {max_id})")
    
    return {
        "name": name,
        "alpha_id": alpha_id,
        "code": code,
        "sharpe": sharpe,
        "fitness": fitness,
        "turnover": turnover,
        "max_corr": max_c,
        "max_corr_id": max_id
    }

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    active_rets = load_active_alphas(session)
    
    experiments = [
        {
            "name": "F11_CallOnly_VolMask",
            "code": "-ts_decay_linear(rank(vwap - close) * rank(volume / adv20) * group_zscore(ts_backfill(implied_volatility_call_20, 20), subindustry), 20)",
            "decay": 20,
            "neut": "SUBINDUSTRY"
        },
        {
            "name": "F11_CallOnly_120",
            "code": "-ts_decay_linear(rank(vwap - close) * group_zscore(ts_backfill(implied_volatility_call_120, 20), subindustry), 20)",
            "decay": 20,
            "neut": "SUBINDUSTRY"
        },
        {
            "name": "F11_PutOnly_VolMask",
            "code": "-ts_decay_linear(rank(vwap - close) * rank(volume / adv20) * group_zscore(ts_backfill(implied_volatility_put_20, 20), subindustry), 20)",
            "decay": 20,
            "neut": "SUBINDUSTRY"
        },
        {
            "name": "F11_PutOnly_120",
            "code": "-ts_decay_linear(rank(vwap - close) * group_zscore(ts_backfill(implied_volatility_put_120, 20), subindustry), 20)",
            "decay": 20,
            "neut": "SUBINDUSTRY"
        },
        {
            "name": "F11_Skew20_Momentum_FastDecay",
            "code": "-ts_decay_linear(rank(close / ts_mean(close, 20)) * group_zscore(ts_backfill(implied_volatility_put_20 - implied_volatility_call_20, 20), subindustry), 5)",
            "decay": 5,
            "neut": "SUBINDUSTRY"
        }
    ]
    
    results = []
    for exp in experiments:
        res = simulate_and_evaluate(
            session, 
            exp["name"], 
            exp["code"], 
            active_rets, 
            exp.get("decay", 20), 
            exp.get("neut", "SUBINDUSTRY"),
            exp.get("universe", "TOP3000")
        )
        if res:
            results.append(res)
        time.sleep(3)
        
    print("\n=======================================================")
    print("PHASE 15 BATCH 11 EXPERIMENT RESULTS:")
    for r in results:
        print(f"[{r['alpha_id']}] {r['name']} | Sh={r['sharpe']:.2f} | Fit={r['fitness']:.2f} | TO={r['turnover']*100:.1f}% | Corr={r['max_corr']:.4f} vs {r['max_corr_id']}")

if __name__ == "__main__":
    main()
