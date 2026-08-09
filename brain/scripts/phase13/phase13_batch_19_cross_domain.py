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
        # --- FAMILY 1: ANALYST TARGET PREMIUM x ASSET EFFICIENCY x INTRADAY ---
        "target_prem_asset_turn_intra_60d": "ts_decay_linear(group_zscore((anl4_target_price_mean - close) / close, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "target_prem_asset_turn_vwap_60d": "ts_decay_linear(group_zscore((anl4_target_price_mean - close) / close, subindustry) * group_zscore(sales / assets, subindustry) * ((close - vwap) / (high - low + 0.001)), 60)",
        "target_prem_gross_profit_intra_60d": "ts_decay_linear(group_zscore((anl4_target_price_mean - close) / close, subindustry) * group_zscore(gross_profit / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        
        # --- FAMILY 2: OPTIONS PCR 90D/60D x NOVY-MARX GROSS PROFITABILITY x PRICE-VOLUME ---
        "pcr90_gross_profit_pv_60d": "ts_decay_linear(group_zscore(put_call_volume_ratio_90 / ts_delay(put_call_volume_ratio_90, 20), subindustry) * group_zscore(gross_profit / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "pcr60_working_cap_intra_60d": "ts_decay_linear(group_zscore(put_call_volume_ratio_60 / ts_delay(put_call_volume_ratio_60, 20), subindustry) * group_zscore(working_capital / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "pcr90_fcf_yield_intra_60d": "ts_decay_linear(group_zscore(put_call_volume_ratio_90 / ts_delay(put_call_volume_ratio_90, 20), subindustry) * group_zscore(fcf / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)",

        # --- FAMILY 3: ANALYST ESTIMATE DISPERSION x CASH FLOW ACCRUALS x GAP REVERSION ---
        "dispersion_accruals_gap_60d": "ts_decay_linear(group_zscore(-((anl4_fs_detail_estimates_basic_af_v4_nd_eps_high - anl4_fs_detail_estimates_basic_af_v4_nd_eps_low) / (abs(anl4_fs_detail_estimates_basic_af_v4_nd_eps_mean) + 0.01)), subindustry) * group_zscore((operating_cash_flow - net_income) / assets, subindustry) * ((open - ts_delay(close, 1)) / (high - low + 0.001)), 60)",
        "dispersion_asset_turn_intra_60d": "ts_decay_linear(group_zscore(-((anl4_fs_detail_estimates_basic_af_v4_nd_eps_high - anl4_fs_detail_estimates_basic_af_v4_nd_eps_low) / (abs(anl4_fs_detail_estimates_basic_af_v4_nd_eps_mean) + 0.01)), subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        
        # --- FAMILY 4: SOCIAL SENTIMENT x EARNINGS QUALITY x INTRADAY DYNAMICS ---
        "sentiment_asset_turn_intra_60d": "ts_decay_linear(group_zscore(snt_social_value_fast_d1, subindustry) * group_zscore(sales / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "sentiment_gross_profit_intra_60d": "ts_decay_linear(group_zscore(snt_social_value_fast_d1, subindustry) * group_zscore(gross_profit / assets, subindustry) * ((close - open) / (high - low + 0.001)), 60)",
        "sentiment_pcr90_asset_turn_60d": "ts_decay_linear(group_zscore(snt_social_value_fast_d1, subindustry) * group_zscore(put_call_volume_ratio_90 / ts_delay(put_call_volume_ratio_90, 20), subindustry) * group_zscore(sales / assets, subindustry), 60)",
        "sentiment_cf_yield_intra_60d": "ts_decay_linear(group_zscore(snt_social_value_fast_d1, subindustry) * group_zscore(operating_cash_flow / enterprise_value, subindustry) * ((close - open) / (high - low + 0.001)), 60)"
    }
    
    results = {}
    print(f"Submitting {len(alphas)} simulations for Phase 13 Batch 19 (Cross-Domain Orthogonals)...")
    for name, code in alphas.items():
        print(f"Submitting {name}...")
        res = simulate_alpha(session, code, name)
        results[name] = res
        time.sleep(3)
        
    out_file = r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\scripts\phase13\phase13_batch_19_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Batch 19 simulation requests saved to {out_file}.")

if __name__ == "__main__":
    main()
