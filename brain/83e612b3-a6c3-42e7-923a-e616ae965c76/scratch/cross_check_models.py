import sys
import os
import re
sys.path.append(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain")
from brain1 import sign_in

def get_user_alphas(session):
    alphas = set()
    for status in ["ACTIVE", "SUBMITTED"]:
        url = f"https://api.worldquantbrain.com/users/self/alphas?status={status}&limit=100"
        while url:
            resp = session.get(url)
            if resp.status_code != 200:
                break
            data = resp.json()
            results = data.get("results", [])
            for a in results:
                alphas.add(a["id"])
            url = data.get("next")
    return alphas

def get_local_alphas(base_dir):
    local_alphas = {}
    for root, dirs, files in os.walk(base_dir):
        if "models" in root:
            for file in files:
                if file.endswith(".md"):
                    match = re.match(r"^([A-Za-z0-9]{8})_", file)
                    if match:
                        alpha_id = match.group(1)
                        local_alphas[alpha_id] = os.path.join(root, file)
    return local_alphas

def main():
    session, _ = sign_in(r"E:\CODING\MMO\wq-brain\WQ-Brainn\brain\brain_credentials.txt")
    api_alphas = get_user_alphas(session)
    print(f"Total ACTIVE/SUBMITTED alphas from API: {len(api_alphas)}")
    
    local_alphas = get_local_alphas(r"E:\CODING\MMO\wq-brain\WQ-Brainn\alpha_insights\phases")
    print(f"Total local models tracked: {len(local_alphas)}")
    
    failed_models = []
    for aid, path in local_alphas.items():
        if aid not in api_alphas:
            failed_models.append((aid, path))
            
    print(f"\nModels that are in local tracking but NOT successful in API: {len(failed_models)}")
    for aid, path in failed_models:
        print(f"Failed/Rejected: {aid} -> {os.path.basename(path)}")

if __name__ == "__main__":
    main()
