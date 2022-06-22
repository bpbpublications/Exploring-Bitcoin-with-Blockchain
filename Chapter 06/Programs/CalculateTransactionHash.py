import hashlib

def getTransactionHash(start: int, end: int, blk_b: bytes): 
    b = blk_b[start: end] 
    h1 = hashlib.sha256(b).digest() 
    h2 = hashlib.sha256(h1).digest() 
    tx_hash = h2[::-1].hex() 
    return tx_hash 
