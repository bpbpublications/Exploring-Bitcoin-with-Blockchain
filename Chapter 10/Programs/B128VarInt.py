def b128_varint_encode(n: int): 
    l = 0 
    b = [] 
    while True: 
        # Take 7 bits and set MSB if not last byte 
        b.append((n & 0x7F)| (0x80 if l != 0 else 0x00)) 
        if n <= 0x7F: 
            break 
        n = (n >> 7) - 1 
        l += 1
    return bytes(bytearray(b[::-1])) 

def b128_varint_decode(b: bytes, pos = 0):
    n = 0
    while True:
        data = b[pos]
        pos += 1
        # unset MSB bit 
        n = (n << 7) | (data & 0x7f)
        if data & 0x80 == 0:
            return (n, pos)
        n += 1
