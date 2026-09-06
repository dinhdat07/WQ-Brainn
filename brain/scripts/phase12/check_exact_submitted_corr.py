import requests
import json
import time

# 1. API details
API_BASE = "https://api.worldquantbrain.com"

# 2. Get credentials
with open("e:/CODING/MMO/wq-brain/wq-alpha-research/credential.txt") as f:
    creds = json.load(f)

# 3. Setup session
session = requests.Session()
session.auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])

print("Authenticating...")
resp = session.post(f"{API_BASE}/authentication")
if resp.status_code not in [200, 201]:
    print(f"Auth failed: {resp.status_code}")
    exit(1)

# The new alpha ID we want to submit
# We will use O07wR2Qq (Decay 30)
TARGET_ALPHA = "O07wR2Qq"

# 4. Fetch previously submitted alphas to get their IDs
print("Fetching previously submitted alphas...")
submitted_alphas = []
limit = 100
offset = 0
while True:
    url = f"{API_BASE}/users/self/alphas?limit={limit}&offset={offset}"
    res = session.get(url)
    if res.status_code != 200:
        print(f"Error fetching alphas: {res.status_code} {res.text}")
        break
    data = res.json()
    results = data.get("results", [])
    if not results:
        break
    for a in results:
        # Check if it was submitted
        if a.get('submit', False) or a.get('status') == 'SUBMITTED' or a.get('is', {}).get('checks', []):
            alpha_id = a.get('id')
            # DON'T add the target alpha itself if it somehow got in there
            if alpha_id != TARGET_ALPHA:
                submitted_alphas.append(alpha_id)
                
    if len(results) < limit:
        break
    offset += limit

print(f"Found {len(submitted_alphas)} submitted alphas to check correlation against.")
if len(submitted_alphas) == 0:
    print("No submitted alphas found. Correlation is trivially 0.")
    exit(0)

# 5. Check correlation for the target alpha against ALL submitted alphas
print(f"Starting correlation check for target alpha {TARGET_ALPHA}...")

# We can query /alphas/{TARGET_ALPHA}/correlations
# It takes a list of alphas to compare with. We might need to chunk if the list is too long.
CHUNK_SIZE = 50
max_corr = 0.0

for i in range(0, len(submitted_alphas), CHUNK_SIZE):
    chunk = submitted_alphas[i:i+CHUNK_SIZE]
    alphas_str = ",".join(chunk)
    corr_url = f"{API_BASE}/alphas/{TARGET_ALPHA}/correlations?alphas={alphas_str}"
    
    retry_count = 0
    while retry_count < 3:
        corr_res = session.get(corr_url)
        if corr_res.status_code == 200:
            corr_data = corr_res.json()
            for record in corr_data.get("records", []):
                val = record.get("value", 0.0)
                if val > max_corr:
                    max_corr = val
            break
        elif corr_res.status_code == 429:
            print("429 limit, sleeping...")
            time.sleep(10)
            retry_count += 1
        elif corr_res.status_code == 401:
            session.post(f"{API_BASE}/authentication")
            retry_count += 1
        else:
            print(f"Error getting correlation: {corr_res.status_code} {corr_res.text}")
            break
    print(f"Processed chunk {i//CHUNK_SIZE + 1} / {(len(submitted_alphas)-1)//CHUNK_SIZE + 1}, current max corr: {max_corr}")

print("\n--- CORRELATION RESULT ---")
print(f"Target Alpha: {TARGET_ALPHA}")
print(f"Maximum Correlation with ANY previously submitted alpha: {max_corr}")
if max_corr > 0.7:
    print("FAILED: Correlation is above 0.70")
else:
    print("PASSED: Correlation is below 0.70. READY FOR SUBMISSION!")
