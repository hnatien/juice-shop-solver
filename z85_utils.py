
import struct

Z85_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#"

def encode(data):
    """
    Encode bytes or string to Z85.
    Input length must be a multiple of 4 bytes (standard Z85).
    If not, we pad with null bytes, but standard Z85 expects exact sizing.
    Juice Shop coupon format: MMMYY-DD (e.g. DEC25-99) = 8 bytes.
    Perfect for 2 chunks of 4 bytes -> 10 chars output.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if len(data) % 4 != 0:
        # Pad with null bytes if necessary, though typical usage here is 8 chars
        padding = (4 - (len(data) % 4)) % 4
        data += b'\0' * padding
        
    result = []
    for i in range(0, len(data), 4):
        chunk = data[i:i+4]
        # Big Endian Unsigned Int
        value = struct.unpack('>I', chunk)[0]
        
        encoded_chunk = []
        for _ in range(5):
            encoded_chunk.append(Z85_CHARS[value % 85])
            value //= 85
        
        # Z85 puts high value char first? 
        # Actually standard Z85: "The divisor is 85..." 
        # Let's verify standard implementation order. Reference: ZeroMQ RFC.
        # "repeatedly dividing by 85... remainder is mapped... output in reverse order" 
        result.append("".join(reversed(encoded_chunk)))
        
    return "".join(result)

def generate_coupon(discount, date=None):
    import datetime
    if not date:
        date = datetime.datetime.now()
    
    # helper for MMMYY
    month = date.strftime('%b').upper()
    year = date.strftime('%y')
    
    # Format: MMMYY-DD (e.g. JAN14-50)
    # Ensure discount is 2 digits? Source code just splits via '-' and parseInt.
    # But length must be multiple of 4 for clean Z85?
    # MMMYY-DD is 3+2+1+2 = 8 chars. Perfect!
    coupon_str = f"{month}{year}-{discount}"
    
    return encode(coupon_str)
