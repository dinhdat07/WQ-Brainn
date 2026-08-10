import sys
import time
import requests

sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def submit_alpha(session, alpha_id):
    print(f"Submitting alpha {alpha_id} to OS...")
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}/submit"
    resp = session.post(url)
    if resp.status_code == 201:
        print("Submission initiated.")
        return True
    elif resp.status_code == 403:
        print("Submission failed (403):", resp.json())
        return False
    else:
        print("Submission failed:", resp.status_code, resp.text)
        return False

def check_submission(session, alpha_id):
    url = f"https://api.worldquantbrain.com/alphas/{alpha_id}"
    for i in range(30):
        resp = session.get(url)
        if resp.status_code == 200:
            status = resp.json().get("status")
            print(f"[{i}] Status: {status}")
            if status in ["PROD", "UNSUBMITTABLE"]:
                print(f"Final status: {status}")
                if status == "UNSUBMITTABLE":
                    checks = resp.json().get("checks", [])
                    for check in checks:
                        if check.get("result") == "FAIL":
                            print(f"Failed check: {check.get('name')}")
                break
        time.sleep(5)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    
    alpha_id = "QPGVEg15"
    if submit_alpha(session, alpha_id):
        check_submission(session, alpha_id)

if __name__ == "__main__":
    main()
