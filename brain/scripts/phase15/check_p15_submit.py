import sys
import json
import time
sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def check_alpha(session, alpha_id):
    resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
    if resp.status_code == 200:
        a = resp.json()
        print(f"[{alpha_id}]")
        print(f"Status: {a.get('status')}")
        print(f"Sharpe: {a.get('is', {}).get('sharpe')}")
        print(f"Fitness: {a.get('is', {}).get('fitness')}")
        print(f"Code: {a.get('regular')}")
        
        # Check checks
        ch_resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}/check")
        if ch_resp.status_code == 200:
            checks = ch_resp.json()
            is_sub = checks.get("isSubmitted", False)
            print(f"Is Submitted: {is_sub}")
            if not is_sub:
                for w in checks.get("warnings", []):
                    print(f"WARNING: {w['name']} - {w.get('message', '')}")
                for e in checks.get("errors", []):
                    print(f"ERROR: {e['name']} - {e.get('message', '')}")
        print("-" * 40)
    else:
        print(f"Error fetching {alpha_id}: {resp.status_code}")

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    check_alpha(session, "leWWY8Oe")
    check_alpha(session, "A1GGmzAg")

if __name__ == "__main__":
    main()
