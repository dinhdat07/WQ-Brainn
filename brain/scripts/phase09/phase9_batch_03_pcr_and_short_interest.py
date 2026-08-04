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
    file_logger.info("Starting Phase 9 Batch 3 - PCR Trigger & Short Interest Decorrelation...")
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
        # 1. PCR Open Interest Trigger + Fundamental Asset Turnover (Additive Blend)
        ("P9_3_PCR_OI_270_Plus_Fund", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry), 10)", 
         {}),

        # 2. PCR Open Interest 180d Triggered Spread
        ("P9_3_PCR_OI_180_Trigger", 
         "ts_decay_linear(group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, (ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)), -1), subindustry), 10)", 
         {}),

        # 3. Short Interest Sentiment: Negative Short Interest Ratio (Low short interest / high institutional conviction)
        ("P9_3_Short_Interest_Ratio", 
         "ts_decay_linear(group_rank(-ts_backfill(shares_sold_short_count_2, 60), subindustry), 10)", 
         {}),

        # 4. Short Interest Ratio x Fast Price Momentum (Short Squeeze Candidate)
        ("P9_3_Short_Squeeze_Combo", 
         "ts_decay_linear(group_rank(ts_backfill(shares_sold_short_count_2, 60), subindustry) * group_rank(close / ts_mean(close, 20), subindustry), 10)", 
         {}),

        # 5. News Bull Trap with Subindustry Neutralization & Decay 15
        ("P9_3_News_Bull_Trap_Subind",
         """
         slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 5, rettype = 2);
         ts_decay_linear(winsorize(-ts_backfill(news_max_up_ret, 60) * abs(slope), std = 4), 15)
         """,
         {"neutralization": "SUBINDUSTRY"})
    ]
    
    file_logger.info(f"Total concepts to process in Phase 9 Batch 3: {len(tasks)}")
    
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
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            sim_status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            file_logger.info(f"[{idx}/{len(tasks)}] {sim_status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit} | TO: {turnover} | Margin: {margin}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
