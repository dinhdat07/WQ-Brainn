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
    file_logger.info("Starting Phase 5 Batch 18 - 10: Quality Fundamentals x Diverse Fast Momentum...")
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
    
    # We use different momentum signals to reduce correlation between the generated alphas
    # Momentum 1: 5d Mean Reversion
    # Momentum 2: 1d Reversion (returns)
    # Momentum 3: 3d Delta Reversion
    # Momentum 4: Intraday Reversion (close/open)
    # Momentum 5: Volume Surprise Reversion
    
    tasks = [
        # 1. ROE + 5d Reversion
        ("18_1_ROE_Reversion", "ts_decay_linear(group_zscore((income / equity) * rank(-(close/ts_mean(close, 5))), subindustry), 5)", {}),
        
        # 2. Profit Margin + 1d Reversion
        ("18_2_Profit_Margin_Reversion", "ts_decay_linear(group_zscore((income / sales) * rank(-returns), subindustry), 5)", {}),
        
        # 3. Cash-to-Assets + 3d Reversion
        ("18_3_Cash_Assets_Reversion", "ts_decay_linear(group_zscore((cash / assets) * rank(-ts_delta(close, 3)), subindustry), 5)", {}),
        
        # 4. Leverage Quality + Intraday Reversion
        ("18_4_Leverage_Reversion", "ts_decay_linear(group_zscore((equity / assets) * rank(-(close/open - 1)), subindustry), 5)", {}),
        
        # 5. Asset Growth Momentum + 5d Reversion
        ("18_5_Asset_Growth_Reversion", "ts_decay_linear(group_zscore((1 / ts_delta(assets, 252)) * rank(-(close/ts_mean(close, 5))), subindustry), 5)", {}),
        
        # 6. Operating Accruals + Volume Surprise Reversion
        ("18_6_Operating_Accruals_Vol", "ts_decay_linear(group_zscore(((assets-cash-liabilities)/assets) * rank(-ts_delta(volume, 5) * sign(returns)), subindustry), 5)", {}),
        
        # 7. ROE x Volume Surprise (Wait, let's use another metric to diversify)
        ("18_7_Operating_Margin_Reversion", "ts_decay_linear(group_zscore((sales / assets) * rank(-returns), subindustry), 5)", {}),
        
        # 8. Cash Flow to Price + Intraday
        ("18_8_CF_Price_Intraday", "ts_decay_linear(group_zscore((cash / close) * rank(-(close/open - 1)), subindustry), 5)", {}),
        
        # 9. Sales Yield + 3d Reversion
        ("18_9_Sales_Yield_Reversion", "ts_decay_linear(group_zscore((sales / (close * sharesout)) * rank(-ts_delta(close, 3)), subindustry), 5)", {}),
        
        # 10. Book Yield + 10d Reversion
        ("18_10_Book_Yield_Reversion", "ts_decay_linear(group_zscore((equity / (close * sharesout)) * rank(-ts_delta(close, 10)), subindustry), 5)", {})
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
