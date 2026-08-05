import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_high_sharpe_alphas():
    alphas = []
    
    # 1. High frequency mean reversion with social buzz volume filter
    alphas.append({
        "name": "HS_MeanRev_SocialVol",
        "regular": "ts_decay_linear(rank(-returns) * rank(ts_backfill(snt_social_volume, 30) / ts_mean(ts_backfill(snt_social_volume, 30), 20)), 5)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 2. Social sentiment divergence from price
    alphas.append({
        "name": "HS_Sent_Price_Div",
        "regular": "ts_decay_linear(rank(ts_backfill(snt_social_value, 30) - ts_mean(ts_backfill(snt_social_value, 30), 20)) * rank(-returns), 5)",
        "settings": {"decay": 0, "neutralization": "SECTOR"}
    })
    
    # 3. Overnight vs Intraday reversal (Classic strong alpha) combined with news sentiment
    alphas.append({
        "name": "HS_Overnight_News",
        "regular": "ts_decay_linear(rank(-1 * (open - ts_delay(close, 1))) * rank(ts_backfill(snt_news_value, 30)), 4)",
        "settings": {"decay": 0, "neutralization": "MARKET"}
    })
    
    # 4. Volatility adjusted mean reversion + Social Value
    alphas.append({
        "name": "HS_VolAdj_Social",
        "regular": "ts_decay_linear(rank(-returns / ts_std_dev(returns, 20)) * rank(ts_backfill(snt_social_value, 30)), 5)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 5. Pure aggressive mean reversion for baseline
    alphas.append({
        "name": "HS_Aggressive_MR",
        "regular": "ts_decay_linear(rank(-returns) * rank(-ts_delta(close, 3)), 3)",
        "settings": {"decay": 0, "neutralization": "SECTOR"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_high_sharpe_alphas()
    print(f"Generated {len(alphas)} High Sharpe Alphas to simulate.")

    simulation_data = {
        "type": "REGULAR",
        "settings": {
            "instrumentType": "EQUITY",
            "region": "USA",
            "universe": "TOP3000",
            "delay": 1,
            "decay": 0,
            "neutralization": "SUBINDUSTRY",
            "truncation": 0.08,
            "pasteurization": "ON",
            "unitHandling": "VERIFY",
            "nanHandling": "ON",
            "language": "FASTEXPR",
            "visualization": False
        },
        "regular": ""
    }

    results = []
    
    for alpha in alphas:
        print(f"\nSimulating: {alpha['name']}")
        
        sim_payload = simulation_data.copy()
        sim_payload["regular"] = alpha["regular"]
        sim_payload["settings"] = {**simulation_data["settings"], **alpha["settings"]}
        
        retries = 3
        while retries > 0:
            try:
                sim_result = brain1.run_simulation(session, sim_payload)
                sim_id = sim_result.get("simulation") or sim_result.get("id")
                
                if sim_id:
                    print(f"Started simulation: {sim_id}")
                    results.append({
                        "name": alpha["name"],
                        "id": sim_id,
                        "formula": alpha["regular"],
                        "settings": sim_payload["settings"],
                        "sim_result": sim_result
                    })
                    break
                else:
                    print(f"Failed to start simulation for {alpha['name']}")
                    print(sim_result)
                    break
            except Exception as e:
                err = str(e)
                print(f"Error simulating {alpha['name']}: {err}")
                if "CONCURRENT_SIMULATION_LIMIT_EXCEEDED" in err:
                    print("Concurrent limit hit! Waiting 30s to retry...")
                    time.sleep(30)
                    retries -= 1
                else:
                    break
            
        time.sleep(2)

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_high_sharpe_pending.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("All submitted successfully.")

if __name__ == "__main__":
    main()
