import struct

# Z85 charset from ZeroMQ spec
Z85_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"
Z85_KV = {c: i for i, c in enumerate(Z85_CHARS)}

def z85_encode(raw_bytes):
    """
    Encode bytes to Z85 string.
    Length of data must be divisible by 4.
    """
    if len(raw_bytes) % 4 != 0:
        # Pad with null bytes if needed, but usually we control the input.
        # For our MMMYY-99 case (e.g. DEC25-99), it is 8 chars?
        # DEC25-99 is 8 bytes.
        raise ValueError("Data length must be multiple of 4")
    
    chars = []
    for i in range(0, len(raw_bytes), 4):
        # Read 4 bytes as 32-bit big-endian integer
        chunk = struct.unpack('>I', raw_bytes[i:i+4])[0]
        
        # Encode to 5 chars
        divisor = 85 * 85 * 85 * 85
        for _ in range(5):
            val = chunk // divisor % 85
            chars.append(Z85_CHARS[val])
            divisor //= 85
            
    return "".join(chars)

def generate_coupon(discount, date=None):
    """
    Generate a Juice Shop coupon code.
    Format: MMMYY-DD (e.g. DEC25-99) encoded in Z85.
    """
    import datetime
    if date is None:
        date = datetime.datetime.now()
    
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    mon = months[date.month - 1]
    year = str(date.year)[2:]
    
    # Format: MMMYY-DD
    # Example: JAN25-99
    # Length check: JAN25-99 is 8 bytes. PERFECT.
    plain = f"{mon}{year}-{discount}"
    if len(plain) != 8:
         # Usually ok for year > 2000 and discount < 100
         pass
         
    return z85_encode(plain.encode('ascii'))
