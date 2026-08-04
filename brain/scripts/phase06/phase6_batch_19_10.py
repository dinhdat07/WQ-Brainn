import os
import sys
import time
import logging

# Add the parent directory to Python path
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
    file_logger.info("Starting Phase 6 Batch 19 - 10: Volatility & Liquidity Anomalies...")
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
        # 1. Amihud Illiquidity Premium
        ("19_1_Amihud_Premium", "ts_decay_linear(group_zscore(abs(returns) / volume, subindustry), 5)", {}),
        
        # 2. Low Volatility Anomaly
        ("19_2_Low_Vol_Anomaly", "ts_decay_linear(group_zscore(-ts_stddev(returns, 20), subindustry), 5)", {}),
        
        # 3. Amihud x Reversion
        ("19_3_Amihud_Reversion", "ts_decay_linear(group_zscore((abs(returns) / volume) * rank(-returns), subindustry), 5)", {}),
        
        # 4. Volatility Adjusted Reversion
        ("19_4_Vol_Adj_Reversion", "ts_decay_linear(group_zscore(-returns / ts_stddev(returns, 20), subindustry), 5)", {}),
        
        # 5. Volume Surprise Reversion
        ("19_5_Vol_Surprise_Rev", "ts_decay_linear(group_zscore(rank(ts_delta(volume, 5)) * sign(-returns), subindustry), 5)", {}),
        
        # 6. High/Low Reversion
        ("19_6_High_Low_Rev", "ts_decay_linear(group_zscore((high + low) / 2 - close, subindustry), 5)", {}),
        
        # 7. Intraday Reversion
        ("19_7_Intraday_Rev", "ts_decay_linear(group_zscore(-(close - open) / open, subindustry), 5)", {}),
        
        # 8. Range Breakout Contrarian
        ("19_8_Range_Contrarian", "ts_decay_linear(group_zscore(-(close - ts_min(low, 20)) / (ts_max(high, 20) - ts_min(low, 20)), subindustry), 5)", {}),
        
        # 9. Volume-Weighted Reversion
        ("19_9_Vol_Weighted_Rev", "ts_decay_linear(group_zscore(-returns * (volume / ts_mean(volume, 20)), subindustry), 5)", {}),
        
        # 10. Amihud 5-Day Reversion
        ("19_10_Amihud_5d_Rev", "ts_decay_linear(group_zscore(rank(abs(returns) / volume) * rank(-ts_delta(close, 5)), subindustry), 5)", {})
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
