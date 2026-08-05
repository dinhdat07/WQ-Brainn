import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_social_opt_alphas():
    alphas = []
    
    # Base formula from Social_Sent_Ret_Mismatch that got 2.06 Sharpe
    base_form = "rank(ts_backfill(snt_social_value, 30)) * rank(-returns)"
    
    # 1. Longer decay
    alphas.append({
        "name": "Social_Opt_Decay20",
        "regular": f"ts_decay_linear({base_form}, 20)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 2. Sector Neutralization
    alphas.append({
        "name": "Social_Opt_NeutSector",
        "regular": f"ts_decay_linear({base_form}, 10)",
        "settings": {"decay": 0, "neutralization": "SECTOR"}
    })
    
    # 3. Market Neutralization
    alphas.append({
        "name": "Social_Opt_NeutMarket",
        "regular": f"ts_decay_linear({base_form}, 10)",
        "settings": {"decay": 0, "neutralization": "MARKET"}
    })
    
    # 4. Filter by high volatility
    alphas.append({
        "name": "Social_Opt_HighVol",
        "regular": f"ts_decay_linear({base_form} * rank(ts_std_dev(returns, 20)), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 5. Filter by high turnover
    alphas.append({
        "name": "Social_Opt_HighTurnover",
        "regular": f"ts_decay_linear({base_form} * rank(turnover), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 6. Group Rank applied to sentiment
    alphas.append({
        "name": "Social_Opt_GroupRank",
        "regular": "ts_decay_linear(group_rank(ts_backfill(snt_social_value, 30), subindustry) * rank(-returns), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 7. Longer window for returns
    alphas.append({
        "name": "Social_Opt_Ret5",
        "regular": "ts_decay_linear(rank(ts_backfill(snt_social_value, 30)) * rank(-ts_delta(close, 5)), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })
    
    # 8. Add value factor (Book to Price)
    alphas.append({
        "name": "Social_Opt_Value",
        "regular": f"ts_decay_linear({base_form} * rank(book_value / equity), 10)",
        "settings": {"decay": 0, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_social_opt_alphas()
    print(f"Generated {len(alphas)} Social Opt Alphas to simulate.")

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

    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_social_opt_pending.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print("All submitted successfully.")

if __name__ == "__main__":
    main()
