import os
import sys
import json
import time
from datetime import datetime

# Add parent directory to path to import brain1
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def generate_news_alphas():
    alphas = []
    
    # Base Bull Trap Logic
    bull_trap_assign = "slope = ts_regression(ts_backfill(news_pct_1min, 60), ts_step(1), 5, rettype = 2);"
    bull_trap_val = "winsorize(-ts_backfill(news_max_up_ret, 60) * abs(slope), std = 4)"
    
    # Variations of Bull Trap
    alphas.append({
        "name": "BullTrap_Decay10_Subindustry",
        "regular": f"{bull_trap_assign} ts_decay_linear(group_rank({bull_trap_val}, subindustry), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    alphas.append({
        "name": "BullTrap_Decay5_Sector",
        "regular": f"{bull_trap_assign} ts_decay_linear(group_rank({bull_trap_val}, sector), 5)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    alphas.append({
        "name": "BullTrap_NoGroup_Decay20",
        "regular": f"{bull_trap_assign} ts_decay_linear({bull_trap_val}, 20)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "SUBINDUSTRY"}
    })
    
    # Sentiment Adjusted Fundamentals
    alphas.append({
        "name": "Sentiment_Composite_OpInc",
        "regular": "ts_decay_linear(group_rank(ts_backfill(composite_sentiment_score_2, 30) * rank(operating_income / equity), subindustry), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    alphas.append({
        "name": "Sentiment_Earnings_OpInc",
        "regular": "ts_decay_linear(group_rank(ts_backfill(earnings_evaluation_sentiment, 30) * rank(operating_income / equity), subindustry), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    alphas.append({
        "name": "Sentiment_Corporate_Assets",
        "regular": "ts_decay_linear(group_rank(ts_backfill(corporate_action_sentiment, 30) * rank(sales / assets), subindustry), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "NONE"}
    })
    
    # Pure Sentiment trend
    alphas.append({
        "name": "Sentiment_Trend_Composite",
        "regular": "ts_decay_linear(ts_regression(ts_backfill(composite_sentiment_score_2, 60), ts_step(1), 20, rettype = 2), 10)",
        "settings": {"decay": 0, "truncation": 0.08, "neutralization": "SUBINDUSTRY"}
    })

    return alphas

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return

    alphas = generate_news_alphas()
    print(f"Generated {len(alphas)} News Microstructure Alphas to simulate.")

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
    with open('E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/phase11_batch01_pending.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
