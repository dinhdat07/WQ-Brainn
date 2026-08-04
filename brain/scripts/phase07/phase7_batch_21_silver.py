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
    file_logger.info("Starting Phase 7 Batch 21 - 11: Silver Alpha Variations...")
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
        # 1. Implied Volatility Spread
        ("21_1_IV_Spread_Base", "ts_decay_linear(trade_when(pcr_oi_270 < 1, (implied_volatility_call_270 - implied_volatility_put_270), -1), 10)", {"neutralization": "MARKET"}),
        ("21_2_IV_Spread_Hint", "ts_decay_linear(group_zscore(trade_when(pcr_oi_270 < 1, (implied_volatility_call_270 - implied_volatility_put_270), -1), bucket(ts_std_dev(returns, 60), range='0, 1, 0.2')), 10)", {}),
        
        # 2. 6-Month Call-Put Volatility Skew
        ("21_3_IV_Skew_Base", "(implied_volatility_call_180 - implied_volatility_put_180) / implied_volatility_mean_180", {"neutralization": "SUBINDUSTRY"}),
        ("21_4_IV_Skew_Hint", "ts_decay_linear(ts_backfill((implied_volatility_call_180 - implied_volatility_put_180) / implied_volatility_mean_180, 20), 10)", {"neutralization": "SUBINDUSTRY"}),
        
        # 3. 5-Day Peer vs. Stock Performance Gap
        ("21_5_Peer_Gap_Base", "cum_rel_return = (1 + ts_delay(rel_ret_all, 4)) * (1 + ts_delay(rel_ret_all, 3)) * (1 + ts_delay(rel_ret_all, 2)) * (1 + ts_delay(rel_ret_all, 1)) * (1 + rel_ret_all); cum_return = (1 + ts_delay(returns, 4)) * (1 + ts_delay(returns, 3)) * (1 + ts_delay(returns, 2)) * (1 + ts_delay(returns, 1)) * (1 + returns); cum_rel_return - cum_return", {"neutralization": "SECTOR"}),
        ("21_6_Peer_Gap_Hint", "cum_rel_return = (1 + ts_delay(rel_ret_all, 4)) * (1 + ts_delay(rel_ret_all, 3)) * (1 + ts_delay(rel_ret_all, 2)) * (1 + ts_delay(rel_ret_all, 1)) * (1 + rel_ret_all); cum_return = (1 + ts_delay(returns, 4)) * (1 + ts_delay(returns, 3)) * (1 + ts_delay(returns, 2)) * (1 + ts_delay(returns, 1)) * (1 + returns); gap = cum_rel_return - cum_return; ts_decay_linear(trade_when(abs(gap) > 0.05, gap, -1), 10)", {"neutralization": "SECTOR"}),
        
        # 4. Investing for the Future
        ("21_7_Invest_Future_Base", "ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2)", {"neutralization": "SUBINDUSTRY"}),
        ("21_8_Invest_Future_Hint", "ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 756, rettype = 2) * group_zscore(ts_delta(sales, 252), subindustry)", {"neutralization": "SUBINDUSTRY"}),
        
        # 5. FCF Quality and Inventory Efficiency Signal
        ("21_9_FCF_Quality_Base", "ts_decay_linear(ts_scale(est_cashflow_op, 252), 22) - ts_decay_linear(ts_scale(est_capex, 252), 22)", {"neutralization": "INDUSTRY"}),
        ("21_10_FCF_Quality_Hint", "fcf = ts_decay_linear(ts_scale(est_cashflow_op, 252), 22) - ts_decay_linear(ts_scale(est_capex, 252), 22); inv_turn = sales / inventory; trade_when(inv_turn / ts_delay(inv_turn, 252) - 1 > 0.5, fcf, -1)", {"neutralization": "INDUSTRY"}),
        
        # 6. Bull Trap
        ("21_11_Bull_Trap", "slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 5, rettype = 2); ts_decay_linear(winsorize(-ts_backfill(news_max_up_ret, 60) * abs(slope), std = 4), 10)", {"neutralization": "INDUSTRY"})
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
