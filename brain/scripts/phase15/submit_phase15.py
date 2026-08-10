import sys
import time
sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def submit_alpha(session, alpha_id):
    print(f"Submitting {alpha_id}...")
    resp = session.post(f"https://api.worldquantbrain.com/alphas/{alpha_id}/submit")
    if resp.status_code == 201:
        print(f"[{alpha_id}] Submitted successfully!")
    elif resp.status_code == 403:
        print(f"[{alpha_id}] Failed to submit: {resp.json().get('message', 'Unknown Error')}")
    else:
        print(f"[{alpha_id}] API Error: {resp.status_code}")

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    # 1. Fundamental Orthogonal (Low Correlation)
    submit_alpha(session, "A1GGmzAg")
    
    time.sleep(2)
    # 2. Options Spectacular (High Sharpe, High Fitness, High Corr)
    submit_alpha(session, "leWWY8Oe")

if __name__ == "__main__":
    main()
