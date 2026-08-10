import sys
import json

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def check_alphas():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    print("Fetching active OS alphas...")
    os_resp = session.get("https://api.worldquantbrain.com/users/self/alphas?limit=50")
    if os_resp.status_code != 200:
        print("Failed to fetch alphas", os_resp.text)
        return
    results = os_resp.json().get("results", [])
    print(f"Total alphas found: {len(results)}")
    for a in results[:20]:
        print(f"{a['id']} - Stage: {a.get('status', 'unknown')}/{a.get('stage', 'unknown')} - color: {a.get('color')}")

if __name__ == "__main__":
    check_alphas()
