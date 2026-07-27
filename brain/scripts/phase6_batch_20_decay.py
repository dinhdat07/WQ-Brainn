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
    file_logger.info("Starting Phase 6 Batch 20 - 12: Turnover Reduction via Decay...")
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
    
    # We take the top 4 models from Batch 19 and apply decay windows of 10, 15, and 20.
    tasks = [
        # Model 5: Vol Surprise Rev (Base Sharpe 2.23, TO 0.76)
        ("20_1_Vol_Surprise_Rev_D10", "ts_decay_linear(group_zscore(rank(ts_delta(volume, 5)) * sign(-returns), subindustry), 10)", {}),
        ("20_2_Vol_Surprise_Rev_D15", "ts_decay_linear(group_zscore(rank(ts_delta(volume, 5)) * sign(-returns), subindustry), 15)", {}),
        ("20_3_Vol_Surprise_Rev_D20", "ts_decay_linear(group_zscore(rank(ts_delta(volume, 5)) * sign(-returns), subindustry), 20)", {}),
        
        # Model 6: High Low Rev (Base Sharpe 1.89, TO 0.75)
        ("20_4_High_Low_Rev_D10", "ts_decay_linear(group_zscore((high + low) / 2 - close, subindustry), 10)", {}),
        ("20_5_High_Low_Rev_D15", "ts_decay_linear(group_zscore((high + low) / 2 - close, subindustry), 15)", {}),
        ("20_6_High_Low_Rev_D20", "ts_decay_linear(group_zscore((high + low) / 2 - close, subindustry), 20)", {}),
        
        # Model 7: Intraday Rev (Base Sharpe 1.88, TO 0.74)
        ("20_7_Intraday_Rev_D10", "ts_decay_linear(group_zscore(-(close - open) / open, subindustry), 10)", {}),
        ("20_8_Intraday_Rev_D15", "ts_decay_linear(group_zscore(-(close - open) / open, subindustry), 15)", {}),
        ("20_9_Intraday_Rev_D20", "ts_decay_linear(group_zscore(-(close - open) / open, subindustry), 20)", {}),
        
        # Model 9: Vol Weighted Rev (Base Sharpe 1.67, TO 0.73)
        ("20_10_Vol_Weighted_Rev_D10", "ts_decay_linear(group_zscore(-returns * (volume / ts_mean(volume, 20)), subindustry), 10)", {}),
        ("20_11_Vol_Weighted_Rev_D15", "ts_decay_linear(group_zscore(-returns * (volume / ts_mean(volume, 20)), subindustry), 15)", {}),
        ("20_12_Vol_Weighted_Rev_D20", "ts_decay_linear(group_zscore(-returns * (volume / ts_mean(volume, 20)), subindustry), 20)", {})
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
                
            alpha_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
            resp = session.get(alpha_url)
            alpha_data = resp.json()
            is_stats = alpha_data.get("is", {})
                
            sharpe = is_stats.get("sharpe", 0)
            fit = is_stats.get("fitness", 0)
            turnover = is_stats.get("turnover", 0)
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            sim_status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            
            file_logger.info(f"[{idx}/{len(tasks)}] {sim_status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit} | TO: {turnover}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
