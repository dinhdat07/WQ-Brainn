import os
import sys
import json
import time

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1
from scripts.phase11.phase11_batch_01_news_microstructure import generate_news_alphas
from scripts.phase11.phase11_batch_02_social_buzz import generate_social_buzz_alphas
from scripts.phase11.phase11_batch_03_peer_relative import generate_peer_relative_alphas

def submit_alphas(session, alphas, batch_name):
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
        print(f"\nSubmitting: {alpha['name']}")
        
        sim_payload = simulation_data.copy()
        sim_payload["regular"] = alpha["regular"]
        sim_payload["settings"] = {**simulation_data["settings"], **alpha["settings"]}
        
        try:
            resp = session.post(brain1.SIMULATE_URL, json=sim_payload, timeout=30)
            if resp.status_code >= 400:
                print(f"Submit failed: {resp.status_code} {resp.text}")
                continue
                
            progress_url = resp.headers.get("Location")
            if progress_url:
                sim_id = progress_url.split('/')[-1]
                print(f"Started simulation: {sim_id}")
                results.append({
                    "name": alpha["name"],
                    "id": sim_id,
                    "formula": alpha["regular"],
                    "settings": sim_payload["settings"]
                })
            else:
                print(f"Failed to get Location header for {alpha['name']}")
        except Exception as e:
            print(f"Error submitting {alpha['name']}: {e}")
            
        time.sleep(1)

    with open(f'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase11/{batch_name}_pending.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    return results

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, user_info = brain1.sign_in(credentials_path)
    if not session:
        print("Login failed!")
        return
        
    news_alphas = generate_news_alphas()
    submit_alphas(session, news_alphas, "phase11_batch01")
    
    social_alphas = generate_social_buzz_alphas()
    submit_alphas(session, social_alphas, "phase11_batch02")
    
    peer_alphas = generate_peer_relative_alphas()
    submit_alphas(session, peer_alphas, "phase11_batch03")
    
    print("All submitted successfully.")

if __name__ == "__main__":
    main()
