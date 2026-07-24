import os
import time
import logging
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain1 import sign_in
from brain3 import run_simulation

logging.basicConfig(filename="logs/assets_optimizer.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Assets Optimizer (from Batch 8/20)...")
    session, _ = sign_in('brain_credentials.txt')
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
        "unitHandling": "VERIFY",
        "nanHandling": "OFF",
        "language": "FASTEXPR",
        "visualization": False,
    }

    # Core from batch 8/20: group_rank(ts_rank(assets, 60), sector)
    # We combine it with various orthogonal price triggers
    tasks = [
        {
            "name": "1_Assets_VWAP_Reversion",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), sector) * ts_rank(vwap - ts_mean(vwap, 5), 5), 3), 30), 5)",
            "neut": "NONE"
        },
        {
            "name": "2_Assets_HighLow_Reversion",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), sector) * ts_rank((high+low)/2 - close, 5), 3), 30), 5)",
            "neut": "NONE"
        },
        {
            "name": "3_Assets_Volume_Exhaustion",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), sector) * ts_rank(ts_delta(volume, 3) * -ts_delta(close, 2), 5), 3), 30), 5)",
            "neut": "NONE"
        },
        {
            "name": "4_Assets_Bollinger_Bounce",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), sector) * ts_rank(ts_mean(close, 10) - close, 10), 3), 30), 5)",
            "neut": "NONE"
        }
    ]

    total = len(tasks)
    file_logger.info(f"Total concepts to process: {total}")
    
    for i, t in enumerate(tasks, 1):
        file_logger.info(f"[{i}/{total}] Submitting {t['name']}: {t['expr']}")
        settings = dict(base_settings)
        settings["neutralization"] = t["neut"]
        
        payload = {"type": "REGULAR", "settings": settings, "regular": t["expr"]}
        
        while True:
            try:
                result = run_simulation(session, payload)
                if result and result.get("status") == "ERROR":
                    file_logger.error(f"[{i}/{total}] SIMULATION ERROR: {result.get('message')}")
                    break
                    
                alpha_id = result.get("alpha") if result else None
                if alpha_id:
                    time.sleep(3)
                    resp = session.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
                    if resp.status_code == 200:
                        stats = resp.json().get('is', {})
                        if stats:
                            sharpe = round(float(stats.get('sharpe', 0)), 2)
                            fitness = round(float(stats.get('fitness', 0)), 2)
                            if sharpe > 1.25 and fitness > 1.0:
                                file_logger.info(f"[{i}/{total}] \U0001f680 SUBMITTABLE! ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness}")
                            else:
                                file_logger.info(f"[{i}/{total}] SUCCESS (Rejected) ID: {alpha_id} | Sharpe: {sharpe} | Fit: {fitness}")
                break
            except Exception as e:
                err_msg = str(e)
                if '429' in err_msg or 'Too Many Requests' in err_msg:
                    file_logger.warning(f"[Run] Hit concurrency limit 429. Sleeping 15s...")
                    time.sleep(15)
                else:
                    file_logger.error(f"[{i}/{total}] EXCEPTION: {e}")
                    break

if __name__ == "__main__":
    main()
