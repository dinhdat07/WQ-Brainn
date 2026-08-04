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
    file_logger.info("Starting Phase 10 Batch 2: Spectacular Alpha Engineering...")
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
        # 1. Quad-Factor Mega Alpha: FCF Quality + Asset Turnover + PCR 270d + Intraday Reversion (Decay 15)
        ("P10_B2_1_Quad_FCF_AssetTurn_PCR270_Intraday_D15", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 15)", 
         {}),

        # 2. Quad-Factor Mega Alpha with Decay 18 (Compacting Turnover to ~7-8%)
        ("P10_B2_2_Quad_FCF_AssetTurn_PCR270_Intraday_D18", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 18)", 
         {}),

        # 3. Quad-Factor Mega Alpha with Decay 20 (Targeting Turnover ~6%)
        ("P10_B2_3_Quad_FCF_AssetTurn_PCR270_Intraday_D20", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 20)", 
         {}),

        # 4. FCF Quality + Asset Turnover + Alpha 101 Intraday Shadow Ratio (Decay 15)
        ("P10_B2_4_FCF_AssetTurn_Alpha101Shadow_D15", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(-(close - open) / ((high - low) + 0.001), subindustry), 15)", 
         {}),

        # 5. FCF Quality + Asset Turnover + Intraday Reversion (Pure Low-Turnover Triad Decay 15)
        ("P10_B2_5_Pure_FCF_AssetTurn_Intraday_D15", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(-(close - open) / open, subindustry), 15)", 
         {}),

        # 6. FCF Quality + Asset Turnover + Intraday Reversion (Decay 18)
        ("P10_B2_6_Pure_FCF_AssetTurn_Intraday_D18", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(-(close - open) / open, subindustry), 18)", 
         {}),

        # 7. Triad 88pomANl with Decay 15 (Optimizing Turnover from 17% down to 10%)
        ("P10_B2_7_Triad_PCR270_AssetTurn_Intraday_D15", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 15)", 
         {}),

        # 8. Quad-Factor with PCR 180d + FCF Quality + Asset Turnover + Intraday (Decay 16)
        ("P10_B2_8_Quad_PCR180_FCF_AssetTurn_Intraday_D16", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_180, 60) < 1, (ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)), -1), subindustry) + group_rank(-(close - open) / open, subindustry), 16)", 
         {})
    ]
    
    file_logger.info(f"Total concepts to process in Phase 10 Batch 2: {len(tasks)}")
    
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
