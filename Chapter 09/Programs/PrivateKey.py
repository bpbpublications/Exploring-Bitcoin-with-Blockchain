import hashlib

g_alphabet='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz' 
g_base_count = len(g_alphabet) 

def hash256(bstr: bytes): 
    return hashlib.sha256(hashlib.sha256(bstr).digest()).digest() 

def base58_encode(num: int): 
    global g_alphabet, g_base_count 
    encode = '' 
    if (num < 0): 
        return '' 
    while (num >= g_base_count): 
        mod = num % g_base_count 
        encode = g_alphabet[mod] + encode 
        num = num // g_base_count 
    if (num >= 0): 
        encode = g_alphabet[num] + encode 
    return encode

def base58checkEncode(prefix: bytes, b: bytes): 
    with_prefix = prefix + b 
    with_checksum = with_prefix + hash256(with_prefix)[0:4] 
    val = int.from_bytes(with_checksum, byteorder='big') 
    encode = base58_encode(val) 
    if prefix == b'\x00': 
        encoded_prefix = base58_encode(0) 
        encode = encoded_prefix + encode 
    return encode 

PRIVKEY_PREFIX_MAINNET=0x80
WIF_PREFIX_MAINNET_COMPRESSED=['L', 'K']
WIF_PREFIX_MAINNET_UNCOMPRESSED=['5']

PRIVKEY_PREFIX_TESTNET=0xEF
WIF_PREFIX_TESTNET_COMPRESSED=['c']
WIF_PREFIX_TESTNET_UNCOMPRESSED=['9']

def encodeWifPrivkey(privkey: int, for_compressed_pubkey: bool):
    prefix_b = bytes.fromhex('%02x' % PRIVKEY_PREFIX_TESTNET)
    privkey_b = bytes.fromhex('%064x' % privkey)
    if for_compressed_pubkey == True:
        privkey_b = privkey_b + b'\01'
    wif_encoded = base58checkEncode(prefix_b, privkey_b)
    return wif_encoded
