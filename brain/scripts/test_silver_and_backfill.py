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
    file_logger.info("Testing ts_backfill fix and Silver Alpha templates...")
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
    
    # 1. Backfilled VolArb + Fundamental
    vol_arb_backfilled = "rank(ts_backfill(implied_volatility_call_120, 60) / ts_backfill(parkinson_volatility_120, 60))"
    fund_rank = "group_rank(sales / assets, subindustry)"
    
    # 2. Silver FCF Quality
    silver_fcf = "ts_decay_linear(ts_scale(ts_backfill(est_cashflow_op, 60), 252) - ts_scale(ts_backfill(est_capex, 60), 252), 22)"
    
    # 3. Silver Peer Gap (Mean Reversion)
    silver_peer_gap = """
    cum_rel = (1 + ts_delay(rel_ret_all, 4)) * (1 + ts_delay(rel_ret_all, 3)) * (1 + ts_delay(rel_ret_all, 2)) * (1 + ts_delay(rel_ret_all, 1)) * (1 + rel_ret_all);
    cum_ret = (1 + ts_delay(returns, 4)) * (1 + ts_delay(returns, 3)) * (1 + ts_delay(returns, 2)) * (1 + ts_delay(returns, 1)) * (1 + returns);
    ts_decay_linear(rank(cum_rel - cum_ret), 5)
    """

    # 4. Silver Volatility Skew with Decay
    silver_vol_skew = "ts_decay_linear(rank((ts_backfill(implied_volatility_call_180, 60) - ts_backfill(implied_volatility_put_180, 60)) / ts_backfill(implied_volatility_mean_180, 60)), 10)"

    tasks = [
        ("VolArb_Backfilled_Add", f"ts_decay_linear({fund_rank} + {vol_arb_backfilled}, 5)", {}),
        ("Silver_VolSkew_Backfilled", silver_vol_skew, {}),
        ("Silver_FCF_Quality", silver_fcf, {"neutralization": "INDUSTRY", "decay": 2}),
        ("Silver_Peer_Gap", silver_peer_gap, {"neutralization": "SECTOR"})
    ]
    
    for idx, (name, expr, overrides) in enumerate(tasks, 1):
        file_logger.info(f"[{idx}/{len(tasks)}] Submitting {name}")
        
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
