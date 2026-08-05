import os
import sys
import json
import time

# Add parent directory to path to import brain1
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_social_buzz_alphas():
    alphas = []
    
    # Logic 1: Social volume spikes combined with positive sentiment
    alphas.append({
        "name": "Social_Vol_Sent_Spike",
        "regular": "ts_decay_linear(group_rank(ts_backfill(snt_social_volume, 30) * ts_backfill(snt_social_value, 30), sector), 5)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    # Logic 2: Fundamental mismatch (high sentiment but recent negative returns)
    alphas.append({
        "name": "Social_Sent_Ret_Mismatch",
        "regular": "ts_decay_linear(rank(ts_backfill(snt_social_value, 30)) * rank(-returns), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "SUBINDUSTRY"}
    })
    
    # Logic 3: Mean Reversion on extreme buzz (using trade_when)
    alphas.append({
        "name": "Social_Buzz_MeanRev",
        "regular": "trade_when(ts_backfill(scl12_buzz, 30) > 0.8, -1, trade_when(ts_backfill(scl12_buzz, 30) < -0.8, 1, 0))",
        "settings": {"decay": 5, "truncation": 0.08, "neutralization": "SUBINDUSTRY"}
    })
    
    # Logic 4: Trend of sentiment z-score
    alphas.append({
        "name": "Social_Sent_Trend",
        "regular": "ts_decay_linear(ts_delta(ts_backfill(snt_social_value, 30), 10), 5)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "SECTOR"}
    })

    # Logic 5: Buzz divergence from volatility
    alphas.append({
        "name": "Social_Buzz_Vol_Div",
        "regular": "ts_decay_linear(rank(ts_backfill(snt_buzz, 30)) - rank(ts_std_dev(returns, 20)), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_social_buzz_alphas()
    print(f"Generated {len(alphas)} Social Buzz Alphas to simulate.")

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
        
        try:
            sim_result = brain1.run_simulation(session, sim_payload)
            sim_id = sim_result.get("simulation") or sim_result.get("id")
            
            if sim_id:
                print(f"Started simulation: {sim_id}")
                results.append({
                    "name": alpha["name"],
                    "id": sim_id,
                    "formula": alpha["regular"],
                    "settings": sim_payload["settings"]
                })
            else:
                print(f"Failed to start simulation for {alpha['name']}")
                print(sim_result)
        except Exception as e:
            print(f"Error simulating {alpha['name']}: {e}")
            
        time.sleep(1)

    print("\nSimulation Submissions Complete. Polling for results...")
    
    # Store pending simulations
    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_batch02_pending.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
