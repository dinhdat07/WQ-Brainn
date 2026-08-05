import os
import sys
import json
import time

# Add parent directory to path to import brain1
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_peer_relative_alphas():
    alphas = []
    
    # Logic 1: Peer Relative EBIT Margin (Subindustry)
    alphas.append({
        "name": "Peer_Rel_EBIT_Margin",
        "regular": "ts_decay_linear(rank(ebit / sales) - group_mean(rank(ebit / sales), 50, subindustry), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    # Logic 2: Peer Relative Analyst Momentum
    alphas.append({
        "name": "Peer_Rel_FScore_Mom",
        "regular": "ts_decay_linear(rank(ts_mean(ts_backfill(fscore_momentum, 30), 20)) - group_mean(rank(ts_mean(ts_backfill(fscore_momentum, 30), 20)), 50, sector), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    # Logic 3: Peer Relative EPS Estimate Trend
    alphas.append({
        "name": "Peer_Rel_EPS_Est_Trend",
        "regular": "trend = ts_regression(ts_backfill(anl4_fs_basic_splt_v4_nd_eps_estimate, 60), ts_step(1), 20, rettype = 2); ts_decay_linear(trend - group_mean(trend, 50, subindustry), 5)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    # Logic 4: Quality Combination (High OpInc, Low Debt) vs Peers
    alphas.append({
        "name": "Peer_Rel_Quality_Combo",
        "regular": "ts_decay_linear(group_rank(operating_income / (equity + 0.001), subindustry) * group_rank(-debt / (equity + 0.001), subindustry), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })

    # Logic 5: Peer Relative Value (Operating Income to Enterprise Value)
    alphas.append({
        "name": "Peer_Rel_Value",
        "regular": "val = operating_income / ((sharesout * close) + debt); ts_decay_linear(rank(val) - group_mean(rank(val), 50, subindustry), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_peer_relative_alphas()
    print(f"Generated {len(alphas)} Peer Relative Alphas to simulate.")

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
    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_batch03_pending.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
