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
    file_logger.info("Starting Phase 10 Batch 1: Spectacular Alpha Hunt...")
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
        # 1. Track 1: Free Cash Flow Quality + Asset Turnover (20d Decay)
        ("P10_1_FCF_Quality_AssetTurn_20d", 
         "ts_decay_linear(group_rank(ts_scale(est_cashflow_op, 252) - ts_scale(est_capex, 252), subindustry) + group_rank(sales / assets, subindustry), 20)", 
         {}),

        # 2. Track 1: FCF Yield + Inventory Velocity (20d Decay)
        ("P10_2_FCF_Yield_InvTurn_20d", 
         "ts_decay_linear(group_rank(ts_zscore((est_cashflow_op - est_capex) / (close * sharesout), 252), subindustry) + group_rank(sales / fnd6_invt, subindustry), 20)", 
         {}),

        # 3. Track 1: Long-Term Investment Trend + Asset Turnover (15d Decay)
        ("P10_3_InvestFuture_AssetTurn_15d", 
         "ts_decay_linear(group_rank(ts_regression(ts_sum(ts_backfill(fnd6_newqv1300_ivltq, 60), 252), ts_step(1), 504, rettype = 2), subindustry) + group_rank(sales / assets, subindustry), 15)", 
         {}),

        # 4. Track 2: Analyst Target Price Momentum + EBIT Value Yield (20d Decay)
        ("P10_4_AnalystPTP_EBIT_Yield_20d", 
         "ts_decay_linear(group_rank(ts_delta(est_ptp, 60) / close, subindustry) + group_rank(est_ebit / (close * sharesout), subindustry), 20)", 
         {}),

        # 5. Track 4: Low-Turnover Institutional Triad Mutation (22d Decay, 5d Reversion)
        ("P10_5_LowTurnover_Triad_22d", 
         "ts_decay_linear(group_rank(sales / assets, subindustry) + group_rank(trade_when(ts_backfill(pcr_oi_270, 60) < 1, (ts_backfill(implied_volatility_call_270, 60) - ts_backfill(implied_volatility_put_270, 60)), -1), subindustry) + group_rank(-ts_delta(close, 5), subindustry), 22)", 
         {}),

        # 6. Track 3: Kakushadze Alpha 54 Reversion + Fundamental Turnover Anchor (20d Decay)
        ("P10_6_Alpha54_AssetTurn_20d", 
         "ts_decay_linear(group_rank((-1 * ((low - close) * (open^5))) / ((low - high) * (close^5)), subindustry) + group_rank(sales / assets, subindustry), 20)", 
         {}),

        # 7. Track 3: Operating Margin Quality + VWAP-Volume Divergence (20d Decay)
        ("P10_7_OpMargin_VWAP_Corr_20d", 
         "ts_decay_linear(group_rank(ebit / sales, subindustry) + group_rank(-ts_corr(vwap, volume, 20), subindustry), 20)", 
         {}),

        # 8. Track 2: Forward EPS Surprise Momentum + Asset Turnover Anchor (20d Decay)
        ("P10_8_EPS_Surprise_AssetTurn_20d", 
         "ts_decay_linear(group_rank(ts_scale(est_eps, 252) - ts_scale(ts_delay(est_eps, 60), 252), subindustry) + group_rank(sales / assets, subindustry), 20)", 
         {})
    ]
    
    file_logger.info(f"Total concepts to process in Phase 10 Batch 1: {len(tasks)}")
    
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
