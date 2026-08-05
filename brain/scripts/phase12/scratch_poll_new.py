import sys
import time
import json
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1
credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
session, _ = brain1.sign_in(credentials_path)

ids = {
    "A6": "3PZ0UHdzZ52z8QZB7IOnGQL"
}

for name, sim_id in ids.items():
    resp = session.get(f"https://api.worldquantbrain.com/simulations/{sim_id}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=4))
