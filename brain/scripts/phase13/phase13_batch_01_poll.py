import os
import sys
import time
import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

def main():
    credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
    session, _ = brain1.sign_in(credentials_path)
    
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    results_file = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/scripts/phase13/phase13_batch_01_results.json'
    
    with open(results_file, 'r') as f:
        alphas = json.load(f)

    pending = [name for name, data in alphas.items() if data.get("status") == "simulating"]
    
    while pending:
        print(f"Checking {len(pending)} pending simulations...")
        for name in pending[:]:
            sim_id = alphas[name]["id"]
            try:
                url = f"https://api.worldquantbrain.com/simulations/{sim_id}"
                resp = session.get(url, timeout=30)
                if resp.status_code == 200:
                    status = resp.json().get("status")
                    if status == "ERROR":
                        print(f"[{name}] ERROR!")
                        alphas[name]["status"] = "ERROR"
                        pending.remove(name)
                    elif status == "COMPLETE":
                        alpha_id = resp.json().get("alpha")
                        alphas[name]["status"] = "COMPLETE"
                        alphas[name]["alpha_id"] = alpha_id
                        print(f"[{name}] COMPLETE! Alpha ID: {alpha_id}")
                        pending.remove(name)
                elif resp.status_code == 404:
                    print(f"[{name}] Not found (404).")
                    alphas[name]["status"] = "NOT_FOUND"
                    pending.remove(name)
                else:
                    print(f"[{name}] Status code {resp.status_code}")
            except Exception as e:
                print(f"[{name}] Error: {e}")
            time.sleep(2)
            
        with open(results_file, 'w') as f:
            json.dump(alphas, f, indent=4)
            
        if pending:
            time.sleep(10)

    print("\nFetching metrics for completed alphas...")
    for name, data in alphas.items():
        if data.get("status") == "COMPLETE" and "metrics" not in data:
            alpha_id = data["alpha_id"]
            try:
                url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
                resp = session.get(url, timeout=30)
                if resp.status_code == 200:
                    metrics = resp.json().get("is", {})
                    data["metrics"] = {
                        "sharpe": metrics.get("sharpe"),
                        "fitness": metrics.get("fitness"),
                        "turnover": metrics.get("turnover"),
                        "margin": metrics.get("margin"),
                        "returns": metrics.get("returns")
                    }
                    print(f"[{name}] Sharpe: {metrics.get('sharpe')} | Fit: {metrics.get('fitness')} | TO: {metrics.get('turnover')}")
            except Exception as e:
                print(f"Error fetching metrics for {name}: {e}")
            time.sleep(2)

    with open(results_file, 'w') as f:
        json.dump(alphas, f, indent=4)
        
    print("\nAll done.")

if __name__ == "__main__":
    main()
