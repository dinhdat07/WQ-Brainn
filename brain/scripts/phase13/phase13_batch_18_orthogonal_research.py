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
        # --- STRATEGY 1: NEWS MICROSTRUCTURE REACTION & DRIFT ---
        "news_5min_reversion_80d": "-ts_decay_linear(group_zscore(ts_backfill(five_minute_price_change_percent, 10), subindustry), 80)",
        "news_high_dev_reversion_40d": "-ts_decay_linear(group_zscore(ts_backfill(high_price_deviation_std_1555, 10), subindustry), 40)",
        "news_vol_ratio_momentum_60d": "ts_decay_linear(group_zscore(ts_backfill(current_to_average_volume_ratio_2, 5), subindustry) * ts_corr(returns, volume, 20), 60)",
        "news_vwap_dev_reversion": "-ts_decay_linear(group_zscore(ts_backfill((close - end_of_day_vwap_3) / close, 10), subindustry), 40)",
        
        # --- STRATEGY 2: ANALYST GUIDANCE & SALES REVISION ORTHOGONALS ---
        "guidance_fcf_yield_80d": "ts_decay_linear(group_zscore(ts_backfill(anl4_fs_guidances_advanced_af_nd_fcf_maxguidance, 60) / close, subindustry), 80)",
        "guidance_ebit_yield_80d": "ts_decay_linear(group_zscore(ts_backfill(anl4_fs_guidances_advanced_af_nd_ebit_minguidance, 60) / close, subindustry), 80)",
        "sales_est_revision_momentum_60d": "ts_decay_linear(group_zscore(ts_delta(ts_backfill(anl4_fs_detail_estimates_basic_qf_v4_nd_sales_median, 20), 20) / close, subindustry), 60)",
        "guidance_fcf_ebit_combo": "ts_decay_linear(group_zscore(ts_backfill(anl4_fs_guidances_advanced_af_nd_fcf_maxguidance + anl4_fs_guidances_advanced_af_nd_ebit_minguidance, 60) / close, subindustry), 80)",

        # --- STRATEGY 3: SHARE DILUTION & STOCK-BASED COMPENSATION DRAG ---
        "sbp_expense_drag_80d": "-ts_decay_linear(group_zscore(ts_backfill(allocated_sbp_expense_total, 250) / close, subindustry), 80)",
        "share_dilution_drag_60d": "-ts_decay_linear(group_zscore(ts_delta(ts_backfill(common_stock_shares_outstanding_count, 60), 60), subindustry), 60)",
        "option_award_dilution_drag": "-ts_decay_linear(group_zscore(ts_backfill(option_award_outstanding_count, 120) / ts_backfill(common_stock_shares_outstanding_count, 120), subindustry), 80)",
        "debt_repayment_strength_60d": "ts_decay_linear(group_zscore(ts_backfill(debt_repayments_total_2, 120) / close, subindustry), 60)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 18...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3) # safe delay
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_18_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 18 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
