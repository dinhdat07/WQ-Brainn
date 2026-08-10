import sys
import json
import time
sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    alpha_id = "ZYEjPlM3"
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/recordsets/pnl"
    resp = session.get(url)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        records = data.get("records", [])
        print(f"Records count: {len(records)}")
        if records:
            print(f"Sample: {records[0]}")
    else:
        print(f"Response: {resp.text}")

if __name__ == "__main__":
    main()
