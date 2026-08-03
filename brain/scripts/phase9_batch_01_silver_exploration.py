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
    file_logger.info("Starting Phase 9 Batch 1 - Silver Alpha Exploration...")
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
        # 1. Silver Theme 2 (Vol Skew 180d, Decay 10)
        ("P9_1_VolSkew_180d_D10", 
         "ts_decay_linear(rank((ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)) / ts_backfill(implied_volatility_mean_180, 60)), 10)", 
         {}),
        
        # 2. Silver Theme 2 (Vol Skew 90d, Decay 10)
        ("P9_2_VolSkew_90d_D10", 
         "ts_decay_linear(rank((ts_backfill(implied_volatility_call_90, 60) - ts_backfill(implied_volatility_put_90, 60)) / ts_backfill(implied_volatility_mean_90, 60)), 10)", 
         {}),

        # 3. Silver Theme 2 (Vol Skew 270d, Decay 15)
        ("P9_3_VolSkew_270d_D15", 
         "ts_decay_linear(rank((ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)) / ts_backfill(implied_volatility_mean_270, 60)), 15)", 
         {}),

        # 4. Silver Theme 2 + Fundamental Combo (Additive)
        ("P9_4_VolSkew_Plus_AssetTurn",
         "ts_decay_linear(group_rank(sales / assets, subindustry) + rank((ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)) / ts_backfill(implied_volatility_mean_180, 60)), 10)",
         {}),

        # 5. Silver Theme 4 (Long-term CapEx Investment Trend)
        ("P9_5_CapEx_LongTerm_Trend",
         "ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2)",
         {"neutralization": "SUBINDUSTRY"}),

        # 6. Silver Theme 5 (Analyst Free Cash Flow Quality with Subindustry Rank)
        ("P9_6_Analyst_FCF_Quality",
         "ts_decay_linear(group_rank(ts_scale(ts_backfill(est_cashflow_op, 60), 252) - ts_scale(ts_backfill(est_capex, 60), 252), subindustry), 15)",
         {"neutralization": "SUBINDUSTRY"}),

        # 7. Silver Theme 6 (News Bull Trap)
        ("P9_7_News_Bull_Trap",
         "slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 5, rettype = 2); winsorize(-ts_backfill(news_max_up_ret, 60) * abs(slope), std = 4)",
         {"neutralization": "INDUSTRY", "decay": 2})
    ]
    
    file_logger.info(f"Total concepts to process in Phase 9 Batch 1: {len(tasks)}")
    
    for idx, (name, expr, overrides) in enumerate(tasks, 1):
        file_logger.info(f"[{idx}/{len(tasks)}] Submitting {name}: {expr.strip()}")
        
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
