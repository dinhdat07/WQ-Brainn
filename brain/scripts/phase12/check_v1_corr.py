import sys
import json
sys.path.append('E:/CODING/MMO/wq-brain/WQ-Brainn/brain')
import brain1

credentials_path = 'E:/CODING/MMO/wq-brain/WQ-Brainn/brain/brain_credentials.txt'
session, _ = brain1.sign_in(credentials_path)

candidate_alpha = "omN2xM9b"
submitted_alphas = [
    "omNZXbA2", "eYw2XJ1o", "8Vpnbb8Q", "JjGlN8zL", "43QK66Kq", 
    "rYN1bb6z", "XvOqEEl9", "6Xpn9V2L", "JjGlRRe9"
]

correlations = []
print(f"Checking {candidate_alpha} against 9 submitted alphas...")
for a2 in submitted_alphas:
    url = f"https://api.worldquantbrain.com/alphas/correlations?alpha1={candidate_alpha}&alpha2={a2}"
    resp = session.get(url)
    if resp.status_code == 200:
        data = resp.json()
        rc = data.get("rc", 0)
        pc = data.get("pc", 0)
        print(f"vs {a2}: rc={rc:.4f}, pc={pc:.4f}")
        correlations.append(rc)
    else:
        print(f"Failed vs {a2}: {resp.status_code} {resp.text}")

if correlations:
    max_rc = max(correlations)
    print(f"\nMAX Return Correlation: {max_rc:.4f}")
    if max_rc < 0.70:
        print("PASS! Alpha is uncorrelated.")
    else:
        print("FAIL! Alpha is too correlated.")
