import json
import requests

API_BASE = "https://api.worldquantbrain.com"
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
session.post(f"{API_BASE}/authentication")

sim_id = "3UyGpz7Gr4VM9SB9YedUlkU"
resp = session.get(f'{API_BASE}/simulations/{sim_id}')
data = resp.json()
print("Alpha ID:", data.get('alpha'))
