import os
import time
import logging
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain1 import sign_in
from brain3 import run_simulation

# truncate the log file on each run so we don't get confused
with open("logs/mutation_optimizer.log", "w") as f:
    f.truncate(0)

logging.basicConfig(filename="logs/mutation_optimizer.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Phase 3 Batch 15 - 10: Optimizing Best Matrix Signals...")
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
        "neutralization": "NONE",
        "truncation": 0.08,
        "pasteurization": "ON",
        "testPeriod": "P2Y",
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "language": "FASTEXPR",
        "visualization": False
    }
    
    tasks = [
        # Signal 1: Target Price Premium (est_ptp / close)
        ("15_1_Target_Price_ZScore_63_Sector", "ts_decay_linear(group_rank(ts_zscore(est_ptp / close, 63), sector), 5)", {}),
        ("15_2_Target_Price_ZScore_126_Industry", "ts_decay_linear(group_rank(ts_zscore(est_ptp / close, 126), industry), 5)", {}),
        ("15_3_Target_Price_ZScore_252_SubInd", "ts_decay_linear(group_zscore(ts_zscore(est_ptp / close, 252), subindustry), 5)", {}),
        ("15_4_Target_Price_ZScore_63_NeutInd", "ts_decay_linear(rank(ts_zscore(est_ptp / close, 63)), 5)", {"neutralization": "Industry"}),
        ("15_5_Target_Price_ZScore_126_NeutMkt", "ts_decay_linear(rank(ts_zscore(est_ptp / close, 126)), 5)", {"neutralization": "Market"}),
        
        # Signal 2: Options Volatility Arbitrage (implied_volatility_call_120 / parkinson_volatility_120)
        ("15_6_OptVol_ZScore_63_Sector", "ts_decay_linear(group_rank(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 63), sector), 5)", {}),
        ("15_7_OptVol_ZScore_126_Industry", "ts_decay_linear(group_rank(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 126), industry), 5)", {}),
        ("15_8_OptVol_ZScore_63_SubInd", "ts_decay_linear(group_zscore(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 63), subindustry), 5)", {}),
        ("15_9_OptVol_ZScore_63_NeutInd", "ts_decay_linear(rank(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 63)), 5)", {"neutralization": "Industry"}),
        ("15_10_OptVol_ZScore_126_NeutMkt", "ts_decay_linear(rank(ts_zscore(implied_volatility_call_120 / parkinson_volatility_120, 126)), 5)", {"neutralization": "Market"})
    ]
    
    file_logger.info(f"Total concepts to process: {len(tasks)}")
    
    for idx, (name, expr, overrides) in enumerate(tasks, 1):
        file_logger.info(f"[{idx}/{len(tasks)}] Submitting {name}: {expr}")
        
        settings = base_settings.copy()
        settings.update(overrides)

        payload = {
            "type": "REGULAR",
            "settings": settings,
            "regular": expr
        }
        
        try:
            body = run_simulation(session, payload)
            
            alpha_id = body.get("alpha")
            if not alpha_id:
                file_logger.error(f"[{idx}/{len(tasks)}] FAILED: No alpha ID returned. Body: {body}")
                continue
                
            # Fetch the alpha to get the stats
            alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
            resp = session.get(alpha_url)
            alpha_data = resp.json()
            is_stats = alpha_data.get("is", {})
            
            if not is_stats:
                file_logger.error(f"[{idx}/{len(tasks)}] FAILED: IS Stats Missing. Alpha Data: {alpha_data}")
                continue
                
            sharpe = is_stats.get("sharpe", 0)
            fit = is_stats.get("fitness", 0)
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            
            file_logger.info(f"[{idx}/{len(tasks)}] {status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
