import os
import sys
import time
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def get_alpha_status(session, sim_id):
    url = f"https://api.worldquantbrain.com/simulations/{sim_id}"
    retries = 3
    while retries > 0:
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                
                if status == "COMPLETE" and "alpha" in data:
                    alpha_id = data["alpha"]
                    # Fetch the alpha metrics
                    alpha_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
                    if alpha_resp.status_code == 200:
                        alpha_data = alpha_resp.json()
                        return "DONE", alpha_data
                    else:
                        return f"ERROR_{alpha_resp.status_code}_ALPHA", None
                return status, data
            elif resp.status_code == 429:
                time.sleep(30)
                retries -= 1
            else:
                return f"ERROR_{resp.status_code}", None
        except:
            retries -= 1
            time.sleep(5)
    return "UNKNOWN", None

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)
    results_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase12/phase12_batch_11_results.json'
    
    if not os.path.exists(results_file):
        print(f"File not found: {results_file}")
        return
        
    with open(results_file, 'r') as f:
        results = json.load(f)
        
    all_done = False
    while not all_done:
        all_done = True
        for name, info in results.items():
            if info["status"] not in ["DONE", "ERROR", "FAIL"]:
                status, data = get_alpha_status(session, info["id"])
                print(f"[{info['id']}] {name}: {status}")
                
                # We map COMPLETE -> DONE inside get_alpha_status if it succeeds in getting alpha
                if status in ["DONE", "ERROR", "FAIL"]:
                    info["status"] = status
                    if status == "DONE" and data and "is" in data:
                        info["sharpe"] = data["is"].get("sharpe")
                        info["fitness"] = data["is"].get("fitness")
                        info["turnover"] = data["is"].get("turnover")
                        info["alpha_id"] = data.get("id")
                else:
                    all_done = False
                time.sleep(3)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)
            
        if not all_done:
            print("Waiting 15 seconds before next poll...")
            time.sleep(15)
            
    print("\n--- Batch 02 Simulation Complete ---")
    for name, info in results.items():
        if info["status"] == "DONE":
            print(f"[{info['id']}] {name}: Sharpe={info.get('sharpe')}, Fitness={info.get('fitness')}, Turnover={info.get('turnover')}")
        else:
            print(f"[{info['id']}] {name}: {info['status']}")

if __name__ == "__main__":
    main()
