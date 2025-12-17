
import hashlib

def crack_md5():
    target_hash = '3c2abc04e4a6ea8f1327d0aae3714b7d'
    print(f"Target Hash: {target_hash}")
    
    # Common passwords
    candidates = [
        '123456', 'password', '123456789', '12345678', '12345', '111111', 
        '1234567', 'sunshine', 'qwerty', 'iloveyou', 'adobe123', '123123', 
        'princess', 'welcome', '0987654321', '098765', 'admin123', 'test1234',
        'start123', 'Job123', 'apple', 'orange', 'banana', 'monkey', 'dragon',
        'football', 'baseball', 'master', 'letmein', 'access', 'juice',
        'JuiceShop', 'bjoern', 'kimminich', 'admin', 'user', 'guest',
        'holiday', 'vacation', 'lovely', 'I<3Juice!', 'foobar'
    ]
    
    # Check 0987654321 specifically
    h = hashlib.md5(b'0987654321').hexdigest()
    print(f"Hash of '0987654321': {h}")
    
    for p in candidates:
        if hashlib.md5(p.encode()).hexdigest() == target_hash:
            print(f"SUCCESS! Password found: {p}")
            return

    # Brute force digits
    print("Brute forcing numeric pins...")
    for i in range(1000000000): # Just a loop, won't run full but maybe small numbers
        s = str(i)
        if hashlib.md5(s.encode()).hexdigest() == target_hash:
             print(f"SUCCESS! Password found (numeric): {s}")
             return
        if i > 500000: break # Stop quickly

if __name__ == '__main__':
    crack_md5()
