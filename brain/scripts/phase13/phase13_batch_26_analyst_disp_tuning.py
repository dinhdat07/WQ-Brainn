import sys
import json
import time
import requests

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def simulate_alpha(session, code, name):
    url = "https://api.worldquantbrain.com/simulations"
    payload = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "OFF",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": code
    }
    
    for attempt in range(5):
        resp = session.post(url, json=payload)
        if resp.status_code == 201:
            sim_loc = resp.headers.get("Location")
            sim_id = sim_loc.split("/")[-1] if sim_loc else ""
            return {"name": name, "code": code, "status": "simulating", "id": sim_id, "sim_url": sim_loc}
        elif resp.status_code == 429:
            time.sleep(10)
        else:
            return {"name": name, "code": code, "status": "error", "error": resp.text}
    return {"name": name, "code": code, "status": "error", "error": "rate_limited"}

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    alphas = {
        # --- 1. DECAY OPTIMIZATION (8d, 12d) ---
        "anl_disp_decay8": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 8)",
        "anl_disp_decay12": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 12)",

        # --- 2. REVISION WINDOW TUNING (60-day, 20-day) ---
        "anl_disp_rev60_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 60) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",
        "anl_disp_rev20_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 20) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",

        # --- 3. QUAD-CORE HYBRIDS (Adding FCF Yield or Working Capital) ---
        "anl_disp_fcf_hybrid_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.6 * group_rank(free_cash_flow_reported_value / cap, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",
        "anl_disp_wc_hybrid_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.6 * group_rank(working_capital / assets, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",

        # --- 4. ANALYST TARGET PRICE UPSIDE GATING ---
        "anl_disp_tp_hybrid_10d": "ts_decay_linear(group_rank(est_ebit / cap, subindustry) + 0.6 * group_rank(est_target_price / close, subindustry) + group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)",

        # --- 5. WEIGHT CONVEXITY / OPTIMAL SENSITIVITY ---
        "anl_disp_convex_10d": "ts_decay_linear(0.8 * group_rank(est_ebit / cap, subindustry) + 1.2 * group_rank(trade_when(group_rank(anl4_fs_detail_estimates_basic_qf_v4_nd_eps_median - anl4_fs_detail_estimates_basic_qf_v4_nd_eps_mean, subindustry) > 0.5, ts_delta(est_ebit, 30) / (abs(est_ebit) + 1), -1), subindustry) + 0.8 * group_rank(-(close - open) / open, subindustry), 10)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 26 (Analyst Dispersion Tuning)...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_26_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 26 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
