import mmap

OP_PUSHDATA1 = 0x4c 
OP_PUSHDATA2 = 0x4d 
OP_PUSHDATA4 = 0x4e 
SIGHASH_ALL = 0x01
SIGHASH_NONE = 0x02
SIGHASH_SINGLE = 0x03
SIGHASH_ANYONECANPAY = 0x80

def getHashTypeInWords(hashtype: int): 
    hashtype_s = "" 
    if hashtype & SIGHASH_SINGLE == 0x03: 
        hashtype_s = "SIGHASH_SINGLE" 
    elif hashtype & SIGHASH_NONE == 0x02: 
        hashtype_s = "SIGHASH_NONE" 
    elif hashtype & SIGHASH_ALL == 0x01: 
        hashtype_s = "SIGHASH_ALL" 
    if hashtype & SIGHASH_ANYONECANPAY == 0x80: 
        hashtype_s = hashtype_s + "|" + "SIGHASH_ANYONECANPAY" 
    return hashtype_s 

def decodePushdata(script_m: mmap): 
    length = int.from_bytes(script_m.read(1), byteorder='little') 
    if length == OP_PUSHDATA1: 
        length = int.from_bytes(script_m.read(1), byteorder='little') 
    elif length == OP_PUSHDATA2: 
        length = int.from_bytes(script_m.read(2), byteorder='little') 
    elif length == OP_PUSHDATA4: 
        length = int.from_bytes(script_m.read(4), byteorder='little') 
    return length 

def parseScriptSig(script_m: mmap): 
    scriptsig = {} 
    scriptsig['bytes_sig'] = decodePushdata(script_m) 
    scriptsig['sig'] = script_m.read(scriptsig['bytes_sig'] - 1).hex() 
    scriptsig['hash_type'] = int.from_bytes(script_m.read(1), byteorder='little') 
    scriptsig['hash_type_name'] = getHashTypeInWords(scriptsig['hash_type']) 
    scriptsig['bytes_pubkey'] = decodePushdata(script_m) 
    scriptsig['pubkey'] = script_m.read(scriptsig['bytes_pubkey']).hex()
    return scriptsig
