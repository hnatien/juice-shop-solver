
import requests
import json

SERVER = 'http://localhost:3000'

def debug_security_question():
    print("Checking Security Question for J12934@juice-sh.op...")
    
    email = 'J12934@juice-sh.op'
    
    s = requests.Session()
    try:
        # Step 1: Get Security Question
        res = s.get(f'{SERVER}/rest/user/security-question', params={'email': email})
        
        if res.ok:
            data = res.json()
            question = data.get('question')
            print(f"Security Question: {question}")
            
            # Step 2: Try to guess answer (OSINT style / Common answers)
            # If no question set, tough luck.
        else:
            print(f"Failed to get security question: {res.status_code}")
            # Maybe user doesn't exist or no question set?
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_security_question()
