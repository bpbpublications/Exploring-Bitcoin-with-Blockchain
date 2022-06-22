from B128VarInt import b128_varint_encode, b128_varint_decode
from ChainstateIndex import applyObfuscationKey

def amount_compress(n: int): 
    if n == 0: 
        return 0; 
    e = 0 
    while ((n % 10) == 0) and e < 9: 
        n //= 10 
        e += 1 
    if e < 9: 
        d = n % 10 
        assert d >= 1 and d <= 9 
        n //= 10 
        return 1 + (n*9 + d - 1)*10 + e 
    else: 
        return 1 + (n - 1)*10 + 9 

def amount_decompress(x): 
    if x == 0: 
        return 0 
    x -= 1 
    e = x % 10 
    x //= 10 
    if e < 9: 
        d = (x % 9) + 1 
        x //= 9 
        n = x * 10 + d 
    else: 
        n = x + 1 
    while e > 0: 
        n *= 10 
        e -= 1 
    return n 

def getUnspentTransactions(tx_hash: bytes, out_index: int,chainstate_db):
    key = b'C' + tx_hash + b128_varint_encode(out_index)
    value_obf_b = chainstate_db.get(key)
    value_obf_b = applyObfuscationKey(value_obf_b, chainstate_db)
    jsonobj = {}
    code, pos = b128_varint_decode(value_obf_b)
    jsonobj['is_coinbase'] = code & 0x01
    jsonobj['block_height'] = code >> 1
    compressed_amount, pos = b128_varint_decode(value_obf_b, pos)
    jsonobj['unspent_amount'] = amount_decompress(compressed_amount)
    jsonobj['script_type'], pos = b128_varint_decode(value_obf_b, pos)
    jsonobj['scriptPubKey']= value_obf_b[pos:].hex()
    return jsonobj
