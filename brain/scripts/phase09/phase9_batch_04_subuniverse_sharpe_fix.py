import os
import sys
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain1 import sign_in
from brain3 import run_simulation

with open("logs/mutation_optimizer.log", "w") as f:
    f.truncate(0)

logging.basicConfig(filename="logs/mutation_optimizer.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Sub-Universe Sharpe Optimization...")
    session, _ = sign_in("brain_credentials.txt")
    if not session:
        print("Auth failed")
        return

    base_settings = {
        "instrumentType": "EQUITY",
        "region": "USA",
        "universe": "TOP3000",
        "delay": 1,
        "decay": 0,
        "neutralization": "SUBINDUSTRY",
        "truncation": 0.05,
        "pasteurization": "ON",
        "testPeriod": "P2Y",
        "unitHandling": "VERIFY",
        "nanHandling": "ON",
        "language": "FASTEXPR",
        "visualization": False
    }
    
    tasks = [
        # 1. Continuous PCR Amplification: Spread / (PCR_OI + 0.1) combined with Asset Turnover
        ("SubUniv_1_PCR_Continuous_Amplification", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) + rank((ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)) / (ts_backfill(pcr_oi_270, 60) + 0.1)), 10)", 
         {}),

        # 2. Multiplicative Interaction: Group Rank Fund * Rank PCR Triggered Spread
        ("SubUniv_2_Multiplicative_Fund_PCR", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) * rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1)), 10)", 
         {}),

        # 3. 3-Pillar Institutional Triad: Fund Turnover + PCR 270d Trigger + Intraday Reversion (Covers all market caps)
        ("SubUniv_3_Triad_Fund_PCR_Intraday", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 10)", 
         {}),

        # 4. Group Z-Score on Fundamental + PCR Trigger (Stronger cross-sectional gradient)
        ("SubUniv_4_GroupZscore_Fund_PCR", 
         "ts_decay_linear(group_zscore(sales / assets, subindustry) + group_zscore(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry), 10)", 
         {}),

        # 5. Continuous PCR 180d Scaled Volatility Skew + Asset Turnover
        ("SubUniv_5_PCR180_Continuous_Fund", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) + rank((ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)) / (ts_backfill(pcr_oi_180, 60) + 0.1)), 10)", 
         {}),

        # 6. 3-Pillar Triad 180d: Fund + PCR 180d Trigger + Fast Delta Reversion
        ("SubUniv_6_Triad_180_DeltaRev", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, (ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)), -1), subindustry) + group_rank(-ts_delta(close, 3), subindustry), 10)", 
         {})
    ]
    
    file_logger.info(f"Total concepts to process in Sub-Universe Optimization: {len(tasks)}")
    
    for idx, (name, expr, overrides) in enumerate(tasks, 1):
        file_logger.info(f"[{idx}/{len(tasks)}] Submitting {name}")
        
        settings = base_settings.copy()
        settings.update(overrides)

        payload = {
            "type": "REGULAR",
            "settings": settings,
            "regular": expr.strip()
        }
        
        try:
            body = run_simulation(session, payload)
            alpha_id = body.get("alpha")
            if not alpha_id:
                file_logger.error(f"[{idx}/{len(tasks)}] FAILED. Body: {body}")
                continue
                
            alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
            resp = session.get(alpha_url)
            alpha_data = resp.json()
            is_stats = alpha_data.get("is", {})
                
            sharpe = is_stats.get("sharpe", 0)
            fit = is_stats.get("fitness", 0)
            turnover = is_stats.get("turnover", 0)
            margin = is_stats.get("margin", 0)
            
            # Check subuniverse metrics if available in alpha_data
            checks = alpha_data.get("is", {}).get("checks", [])
            sub_sharpe_info = [c for c in checks if "SUB_UNIVERSE_SHARPE" in str(c.get("name", "")).upper()]
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            sim_status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            file_logger.info(f"[{idx}/{len(tasks)}] {sim_status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit} | TO: {turnover} | Margin: {margin} | SubChecks: {sub_sharpe_info}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
