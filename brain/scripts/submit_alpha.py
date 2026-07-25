import os
import sys
import json
import requests
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brain1 import sign_in

def submit_alpha(alpha_id):
    session, _ = sign_in('brain_credentials.txt')
    if not session:
        print("Auth failed")
        return
    
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/submit"
    
    print(f"Submitting alpha {alpha_id}...")
    resp = session.post(url)
    
    if resp.status_code >= 400:
        print(f"Failed to submit: {resp.status_code} {resp.text}")
        return
        
    print(f"Submit Request Accepted: {resp.status_code}")
    print("Wait for the self-correlation test to finish...")
    
    for _ in range(10):
        time.sleep(5)
        check_url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
        chk_resp = session.get(check_url)
        if chk_resp.status_code == 200:
            data = chk_resp.json()
            status = data.get("status", "UNKNOWN")
            print(f"Status: {status} | Self-Correlation Check...")
            if status in ["UNSUBMITTED", "FAIL"]:
                print("Submission failed or rejected.")
                break
            elif status == "APPROVED":
                print("SUCCESS! Alpha passed all tests including self-correlation!")
                break
        else:
            print("Check failed:", chk_resp.status_code)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        submit_alpha(sys.argv[1])
    else:
        print("Usage: python submit_alpha.py <alpha_id>")
