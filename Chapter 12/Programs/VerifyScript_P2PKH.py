import json
import mmap
import struct
import hashlib
import ecdsa
from ParseScriptSig import decodePushdata
from FindTransactionInLevelDB import findTransaction, txindex_db_g
from AddressGenerationPKH import hash256, hash160
from cryptotools.ECDSA.secp256k1 import PublicKey

st = [] 

def opHash160(): 
    v = st.pop() 
    h = hash160(v) 
    st.append(h) 

def opDup(): 
    v = st.pop() 
    st.append(v) 
    st.append(v) 

def opEqualVerify(): 
    v1 = st.pop() 
    v2 = st.pop() 
    if v1 == v2: 
        return True 
    else: 
        return False 

g_pushdata = range(0x01, 0x4f)

def pushdata(d: bytes): 
    st.append(d) 

def opCheckSig(script_b: bytes, inp_index: int, tx: dict): 
    pubkey_b = st.pop() 
    sig_b = st.pop() 
    v = sigcheck(sig_b, pubkey_b, script_b, inp_index, tx) 
    st.append(v)

def execScript(script_b: bytes, inp_index: int, tx: dict): 
    l = len(script_b) 
    script_m = bytes2Mmap(script_b) 
    while script_m.tell() < l: 
        v = script_m.read(1) 
        b = int.from_bytes(v, byteorder='little') 
        if b in g_pushdata: 
            script_m.seek(-1, 1) 
            b = decodePushdata(script_m) 
            d = script_m.read(b) 
            pushdata(d) 
        elif v == b'\x76': 
            opDup() 
        elif v == b'\xa9': 
            opHash160() 
        elif v == b'\x88': 
            opEqualVerify() 
        elif v == b'\xac': 
            opCheckSig(script_b, inp_index, tx) 

def getRandSFromSig(sig_b: bytes):
    sig_m = bytes2Mmap(sig_b)
    struct = sig_m.read(1)
    size = sig_m.read(1)
    rheader = sig_m.read(1)
    rsize_b = sig_m.read(1)
    rsize = int.from_bytes(rsize_b, byteorder='little')
    if rsize == 33:
        sig_m.read(1)
    r = sig_m.read(32)
    sheader = sig_m.read(1)
    ssize_b = sig_m.read(1)
    ssize = int.from_bytes(ssize_b, byteorder='little')
    if ssize == 33:
        sig_m.read(1)
    s = sig_m.read(32)
    return r + s

def bytes2Mmap(b: bytes):
    m = mmap.mmap(-1, len(b) + 1)
    m.write(b)
    m.seek(0)
    return m

def setVarInt(n: int):
    if n < 0xfd:
        n_h = '%02x' % n
    elif n > 0xfd and n < 0xffff:
        n_h = 'fd%04x' % n
    elif n > 0xffff and n < 0xFFFFFFFF:
        n_h = 'fe%08x' % n
    else:
        n_h = 'ff%016x' % n
    return bytes.fromhex(n_h)

def createMsgInputsForSig(tx: dict, script_b: bytes,
                        inp_index: int, sighash_type: int,
                        inp_cnt: int):
    msg_b = b''
    for i in range(inp_cnt):
        tx_inp = tx['inputs'][i]
        inp_b = bytes.fromhex(tx_inp['prev_tx_hash'])[::-1]
        inp_b += struct.pack('<L', tx_inp['prev_tx_out_index'])
        if i == inp_index:
            inp_b += bytes.fromhex('%02x' % len(script_b))
            inp_b += script_b
            inp_b += struct.pack('<L', tx_inp['sequence']) # sequence
        else:
            inp_b += bytes(1)
            inp_b += struct.pack('<L', tx_inp['sequence']) # sequence
        msg_b += inp_b
    return msg_b

def createMsgOutsForSig(tx: dict, inp_index: int, sighash_type: int):
    msg_b = b''
    msg_b += setVarInt(tx['out_cnt'])
    for o in range(tx['out_cnt']):
        tx_out = tx['outs'][o]
        msg_b += struct.pack('<Q', tx_out['satoshis'])
        msg_b += setVarInt(tx_out['bytes_scriptpubkey'])
        msg_b += bytes.fromhex(tx_out['scriptpubkey'])
    return msg_b

def createMsgForSig(tx: dict, script_b: bytes, inp_index: int, sighash_type: int):
    global txindex_db_g
    msg_b = bytes.fromhex(tx['version'])[::-1]
    inp_cnt = tx['inp_cnt']
    msg_b += setVarInt(inp_cnt)
    msg_b += createMsgInputsForSig(tx, script_b, inp_index, sighash_type, inp_cnt)
    msg_b += createMsgOutsForSig(tx, inp_index, sighash_type)
    msg_b += struct.pack('<L', tx['locktime'])
    msg_b += struct.pack('<L', sighash_type)
    return msg_b

def uncompressPubkey(pubkey_b: bytes):
    pubkey_P = PublicKey.decode(pubkey_b)
    pubkey_b = PublicKey.encode(pubkey_P, compressed=False)
    return pubkey_b

def sigcheck(sig_b: bytes, pubkey_b: bytes, script_b: bytes, inp_index: int, tx: dict):
    sighash_type = sig_b[-1]
    msg_b = createMsgForSig(tx, script_b, inp_index, sighash_type)
    msg_h = hashlib.sha256(msg_b).digest()
    prefix = pubkey_b[0:1]
    if prefix == b"\x02" or prefix == b"\x03":
        fullpubkey_b = uncompressPubkey(pubkey_b)[1:]
    elif prefix == b"\x04":
        fullpubkey_b = pubkey_b[1:]
    rs_b = getRandSFromSig(sig_b)
    vk = ecdsa.VerifyingKey.from_string(fullpubkey_b, curve=ecdsa.SECP256k1)
    try:
        if vk.verify(rs_b, msg_h, hashlib.sha256) == True:
            print("Signature is Valid")
            return b'\x01'
        else:
            print("Signature is not Valid")
            return b'\x00'
    except ecdsa.keys.BadSignatureError:
        print("Signature is not Valid")
        return b'\x00'

def getScriptSig(tx: dict, inp_index: int): 
    return bytes.fromhex(tx['inputs'][inp_index]['scriptsig']) 

def getPrevScriptPubKey(tx: dict, inp_index: int): 
    prevtx_rb = bytes.fromhex(tx['inputs'][inp_index]['prev_tx_hash'])[::-1] 
    print('prevtx = ', tx['inputs'][inp_index]['prev_tx_hash'])
    prevtx_outindex = tx['inputs'][inp_index]['prev_tx_out_index'] 
    print('prevtx_outindex = ', prevtx_outindex)
    prevtx = findTransaction(prevtx_rb, txindex_db_g) 
    print(json.dumps(prevtx, indent=4))
    prevScriptPubkey = prevtx['outs'][prevtx_outindex]['scriptpubkey'] 
    prevScriptPubkey_b = bytes.fromhex(prevScriptPubkey) 
    return prevScriptPubkey_b 

def verifyScript(tx: dict, inp_index: int): 
    scriptsig_b = getScriptSig(tx, inp_index) 
    execScript(scriptsig_b, inp_index, tx) 
    prev_scriptpubkey_b = getPrevScriptPubKey(tx, inp_index) 
    execScript(prev_scriptpubkey_b, inp_index, tx) 
    status = st.pop() 
    if status == b'\x01': 
        print('1st Script succeeded') 
    elif status == b'\x01': 
        print('1st Script Failed') 
    else: 
        print('1st Invalid state') 

