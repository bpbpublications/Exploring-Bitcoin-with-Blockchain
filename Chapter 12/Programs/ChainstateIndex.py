import os
import plyvel

chainstate_db_g = plyvel.DB(os.getenv('CHAINSTATE_DB'), compression=None) 

def getObfuscationKey(chainstate_db): 
    value = chainstate_db.get(b'\x0e\x00' + b'obfuscate_key') 
    print('obfuscation key = %s' % value) 
    obfuscation_key = value[1:] 
    return obfuscation_key 

def applyObfuscationKey(data: bytes, chainstate_db): 
    obfuscation_key = getObfuscationKey(chainstate_db) 
    new_val = bytes(data[index] ^ obfuscation_key[index % len(obfuscation_key)] for index in range(len(data))) 
    return new_val 

def getRecentBlockHash(chainstate_db):
    key = b'B'
    block_hash_b = chainstate_db.get(key)
    block_hash_b = applyObfuscationKey(block_hash_b, chainstate_db)
    return block_hash_b
