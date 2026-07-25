import os
import time
import logging
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brain1 import sign_in
from brain3 import run_simulation

logging.basicConfig(filename="logs/mutation_optimizer.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
file_logger = logging.getLogger(__name__)

def main():
    file_logger.info("Starting Mutation Optimizer...")
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

    # Testing mutated price triggers to break correlation with ZYKo6R78 (-ts_delta(close, 3))
    tasks = [
        # Nhánh 1: HighLow Reversion (đã từng đạt Sharpe 1.33 nhưng Fit 0.94) -> Cải tiến decay cuối cùng lên 8 hoặc 10
        {
            "name": "1_Assets_HighLow_Decay8",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), subindustry) * ts_rank((high+low)/2 - close, 5), 4), 30), 8)",
            "neut": "NONE"
        },
        {
            "name": "2_Assets_HighLow_Decay10",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), subindustry) * ts_rank((high+low)/2 - close, 5), 4), 30), 10)",
            "neut": "NONE"
        },
        # Nhánh 2: Intraday Reversion (-(close/open - 1))
        {
            "name": "3_Assets_Intraday_Reversion",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(assets, 60), subindustry) * ts_rank(-(close/open - 1), 5), 3), 30), 8)",
            "neut": "NONE"
        },
        # Nhánh 3: Sales + Intraday Reversion
        {
            "name": "4_Sales_Intraday_Reversion",
            "expr": "ts_decay_linear(ts_zscore(ts_decay_linear(group_rank(ts_rank(sales, 60), subindustry) * ts_rank(-(close/open - 1), 5), 3), 30), 8)",
            "neut": "NONE"
        },
        # Nhánh 4: Alternative Data (Sentiment) không dùng Z-score, nhưng dùng High Decay
        {
            "name": "5_Sentiment_Alternative",
            "expr": "ts_decay_linear(group_rank(ts_rank(mean_composite_sentiment_score, 60), subindustry) * ts_rank(-ts_delta(close, 5), 5), 15)",
            "neut": "NONE"
        },
        # Nhánh 5: Analyst EBIT Reversion không dùng Z-score
        {
            "name": "6_Analyst_Alternative",
            "expr": "ts_decay_linear(group_rank(ts_rank(anl4_fs_detail_estimate_1qf_v4_nd_ebit_mean, 60), subindustry) * ts_rank(-ts_delta(close, 5), 5), 15)",
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
