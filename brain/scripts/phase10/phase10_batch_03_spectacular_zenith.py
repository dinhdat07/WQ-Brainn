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
    file_logger.info("Starting Phase 10 Batch 3: Spectacular Zenith Optimization...")
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
        # 1. Fundamental-Weighted Quad Factor (2x Fund, 2x AssetTurn, 1x PCR, 1x Intraday) Decay 20
        ("P10_B3_1_FundWeighted_Quad_D20", 
         "ts_decay_linear(2 * group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + 2 * group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 20)", 
         {}),

        # 2. Fundamental-Weighted Quad Factor Decay 22 (Compressing Turnover to ~6-7%)
        ("P10_B3_2_FundWeighted_Quad_D22", 
         "ts_decay_linear(2 * group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + 2 * group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 22)", 
         {}),

        # 3. Fundamental-Weighted Quad Factor Decay 25 (Compressing Turnover to ~5-6%)
        ("P10_B3_3_FundWeighted_Quad_D25", 
         "ts_decay_linear(2 * group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + 2 * group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 25)", 
         {}),

        # 4. Quad-Factor with Standardized Group Z-Scores Decay 20
        ("P10_B3_4_GroupZScore_Quad_D20", 
         "ts_decay_linear(group_zscore(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_zscore(sales / assets, subindustry) + group_zscore(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_zscore(-(close - open) / open, subindustry), 20)", 
         {}),

        # 5. Quad-Factor with Standardized Group Z-Scores Decay 22
        ("P10_B3_5_GroupZScore_Quad_D22", 
         "ts_decay_linear(group_zscore(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_zscore(sales / assets, subindustry) + group_zscore(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_zscore(-(close - open) / open, subindustry), 22)", 
         {}),

        # 6. Quad-Factor: FCF Quality + Asset Turnover + Analyst Revision + Intraday Reversion Decay 20
        ("P10_B3_6_FCF_AssetTurn_AnalystPTP_Intraday_D20", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(ts_delta(est_ptp, 60) / close, subindustry) + group_rank(-(close - open) / open, subindustry), 20)", 
         {}),

        # 7. Penta-Factor Mega Alpha: FCF Quality + AssetTurn + PCR270 + Analyst Revision + Intraday Decay 22
        ("P10_B3_7_Penta_Mega_D22", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(ts_delta(est_ptp, 60) / close, subindustry) + group_rank(-(close - open) / open, subindustry), 22)", 
         {}),

        # 8. Quad Factor Equal Weight Decay 24 (Targeting Turnover ~7.5%)
        ("P10_B3_8_Quad_EqualWeight_D24", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 24)", 
         {})
    ]
    
    file_logger.info(f"Total concepts to process in Phase 10 Batch 3: {len(tasks)}")
    
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
            returns = is_stats.get("returns", 0)
            drawdown = is_stats.get("drawdown", 0)
            
            checks = alpha_data.get("is", {}).get("checks", [])
            sub_sharpe_info = [c for c in checks if "SUB_UNIVERSE_SHARPE" in str(c.get("name", "")).upper()]
            
            if sharpe is None: sharpe = 0
            if fit is None: fit = 0
            
            sim_status = "SUCCESS" if sharpe > 1.25 and fit > 1.0 else "SUCCESS (Rejected)"
            file_logger.info(f"[{idx}/{len(tasks)}] {sim_status} ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fit} | TO: {turnover} | Margin: {margin} | Ret: {returns} | DD: {drawdown} | SubChecks: {sub_sharpe_info}")
            
        except Exception as e:
            file_logger.error(f"[{idx}/{len(tasks)}] Exception: {str(e)}")
            
        time.sleep(2)

if __name__ == "__main__":
    main()
