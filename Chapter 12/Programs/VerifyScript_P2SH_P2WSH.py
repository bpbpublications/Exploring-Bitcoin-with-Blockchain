import json
import struct
import hashlib
import ecdsa
from VerifyScript_P2PKH import getScriptSig, bytes2Mmap, \
        decodePushdata, pushdata
from FindTransactionInLevelDB import findTransaction, txindex_db_g
from AddressGenerationPKH import hash256, hash160
from cryptotools.ECDSA.secp256k1 import PublicKey, PrivateKey, Point, G, P, N, CURVE

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

def getAmountFromPrevout(prev_tx_hash_b: bytes, prev_tx_out_index_b: bytes):
    prevtx = findTransaction(prev_tx_hash_b, txindex_db_g)
    prevtx_outindex = int.from_bytes(prev_tx_out_index_b, byteorder = 'little')
    prevAmount = prevtx['outs'][prevtx_outindex]['satoshis']
    amount_b = struct.pack("<Q", prevAmount)
    return amount_b

def createMsgForSigForSegwit(tx: dict, script_b: bytes, inp_index: int, sighash_type: int):
    version_b = bytes.fromhex(tx['version'])[::-1]
    inp_cnt = tx['inp_cnt']
    prevouts_b = b''
    sequences_b = b''
    for i in range(inp_cnt):
        tx_inp = tx['inputs'][i]
        prev_tx_hash_b = bytes.fromhex(tx_inp['prev_tx_hash'])[::-1]
        prev_tx_out_index_b = struct.pack('<L', tx_inp['prev_tx_out_index'])
        sequences_b += struct.pack('<L', tx_inp['sequence'])
        prevouts_b += prev_tx_hash_b + prev_tx_out_index_b
        if i == inp_index:
            outpoint_b = prev_tx_hash_b + prev_tx_out_index_b
            print('script = ', script_b.hex())
            scriptCode_b = bytes.fromhex('%x' % len(script_b)) + script_b
            amount_b = getAmountFromPrevout(prev_tx_hash_b, prev_tx_out_index_b)
            sequence_b = struct.pack('<L', tx_inp['sequence'])
    out_cnt = tx['out_cnt']
    outputs_b = b''
    for o in range(out_cnt):
        tx_out = tx['outs'][o]
        satoshis_b = struct.pack('<Q', tx_out['satoshis'])
        bytes_scriptpubkey_b = setVarInt(tx_out['bytes_scriptpubkey'])
        scriptpubkey_b = bytes.fromhex(tx_out['scriptpubkey'])
        outputs_b += satoshis_b + bytes_scriptpubkey_b + scriptpubkey_b
    locktime_b = struct.pack('<L', tx['locktime'])
    hashPrevouts_b = hash256(prevouts_b)
    hashSequence_b = hash256(sequences_b)
    hashOutputs_b = hash256(outputs_b)
    hashType_b = struct.pack('<L', sighash_type)
    msg_b = version_b + hashPrevouts_b + hashSequence_b + outpoint_b + scriptCode_b + amount_b + sequence_b + hashOutputs_b + locktime_b + hashType_b
    return msg_b

def uncompressPubkey(pubkey_b: bytes):
    pubkey_P = PublicKey.decode(pubkey_b)
    pubkey_b = PublicKey.encode(pubkey_P, compressed=False)
    return pubkey_b

def sigcheck(sig_b: bytes, pubkey_b: bytes,  
            script_b: bytes, inp_index: int, tx: dict): 
    sighash_type = sig_b[-1] 
    if tx['is_segwit'] == True: 
        msg_b = createMsgForSigForSegwit(tx, script_b, inp_index, sighash_type) 
    else: 
        msg_b = createMsgForSig(tx, script_b, inp_index, sighash_type) 
    print('sig = %s' % sig_b.hex()) 
    print('pubkey = %s' % pubkey_b.hex()) 
    print('msg = %s' % msg_b.hex()) 
    msg_h = hashlib.sha256(msg_b).digest()
    print('msg_h = %s' % msg_h.hex()) 
    prefix = pubkey_b[0:1] 
    if prefix == b"\x02" or prefix == b"\x03": 
        fullpubkey_b = uncompressPubkey(pubkey_b)[1:] 
    elif prefix == b"\x04": 
        fullpubkey_b = pubkey_b[1:] 
    rs_b = getRandSFromSig(sig_b) 
    print('rs = %s' % rs_b.hex()) 
    vk = ecdsa.VerifyingKey.from_string(fullpubkey_b, curve=ecdsa.SECP256k1) 
    if vk.verify(rs_b, msg_h, hashlib.sha256) == True: 
        print("Signature is Valid") 
        return b'\x01' 
    else: 
        print("XXXXXXSignature is not Valid") 
        return b'\x00' 

g_pushnumber = range(0x51, 0x61) # excludes 0x61

def opEqual():
    v1 = st.pop()
    v2 = st.pop()
    if v1 == v2:
        st.append(b'\x01')
    else:
        st.append(b'\x00')

def opNum(b: int):
    num = b - 0x50
    st.append(bytes([num]))

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

def opCheckMultisig(script_b: bytes, inp_index: int, tx: dict):
    pubkey_cnt = int.from_bytes(st.pop(), byteorder='little')
    pubkey_l = [st.pop() for i in range(pubkey_cnt)][::-1]
    sig_cnt = int.from_bytes(st.pop(), byteorder='little')
    sig_l = [st.pop() for i in range(sig_cnt)][::-1]
    sig_index = 0
    for pubkey_b in pubkey_l:
        v = sigcheck(sig_l[sig_index], pubkey_b, script_b, inp_index, tx)
        if v == b'\x01':
            sig_index += 1
            if sig_index == sig_cnt:
                break
    # convert True/False to b'\x01' or b'\x00'
    b = bytes([int(sig_index == sig_cnt and v == b'\x01')])
    st.append(b)

def pushWitnessData(witness_l: list): 
    for data in witness_l: 
        st.append(bytes.fromhex(data['witness'])) 

def getWitnessList(tx: dict, inp_index: int): 
    return tx['inputs'][inp_index]['witnesses'] 

def checkWrappedMultisig(st): 
    script_b = st[-1] 
    val = script_b[-2] 
    if bytes([script_b[-1]]) == b'\xae' and val in g_pushnumber: 
        return True 
    else: 
        return False 

def checkWrappedP2WPKH(st): 
    script_b = st[-1] 
    if script_b[:2] == b'\x00\x14' and len(script_b) == 22: 
        return True 
    else: 
        return False 

def checkWrappedP2WSH(st):
    script_b = st[-1] 
    if script_b[:2] == b'\x00\x20' and len(script_b) == 34: 
        return True 
    else: 
        return False 

def isP2WPKH(prev_scriptpubkey_b: bytes): 
    #0014<20 bytes> 
    if len(prev_scriptpubkey_b) == 22 and prev_scriptpubkey_b[0:2] == b'\x00\x14': 
        return True 
    return False 

def isP2WSH(prev_scriptpubkey_b: bytes):
    #0020<32 bytes>
    if len(prev_scriptpubkey_b) == 34 and prev_scriptpubkey_b[0:2] == b'\x00\x20':
        return True
    return False

def opSha256():
    v = st.pop()
    h = hashlib.sha256(v).digest()
    st.append(h)

def execScript(script_b: bytes, inp_index: int, tx: dict):
    l = len(script_b)
    script_m = bytes2Mmap(script_b)
    while script_m.tell() < l:
        v = script_m.read(1)
        b = int.from_bytes(v, byteorder='big')
        if b in g_pushdata:
            script_m.seek(-1, 1)
            b = decodePushdata(script_m)
            d = script_m.read(b)
            pushdata(d)
        elif v == b'\x76':
            opDup()
        elif v == b'\xa8':
            opSha256()
        elif v == b'\xa9':
            opHash160()
        elif b in g_pushnumber:
            opNum(b)
        elif v == b'\x87':
            opEqual()
        elif v == b'\x88':
            opEqualVerify()
        elif v == b'\xac':
            opCheckSig(script_b, inp_index, tx)
        elif v == b'\xae':
            opCheckMultisig(script_b, inp_index, tx)

def getPrevScriptPubKey(tx: dict, inp_index: int):
    prevtx_rb = bytes.fromhex(tx['inputs'][inp_index]['prev_tx_hash'])[::-1]
    prevtx_outindex = tx['inputs'][inp_index]['prev_tx_out_index']
    prevtx = findTransaction(prevtx_rb, txindex_db_g)
    prevScriptPubkey = prevtx['outs'][prevtx_outindex]['scriptpubkey']
    prevScriptPubkey_b = bytes.fromhex(prevScriptPubkey)
    return prevScriptPubkey_b

def verifyScript(tx: dict, inp_index: int):
    scriptsig_b = getScriptSig(tx, inp_index)
    if scriptsig_b == b'':
        # native segwit
        print('native segwit')
        witness_l = getWitnessList(tx, inp_index)
        pushWitnessData(witness_l)
    else:
        execScript(scriptsig_b, inp_index, tx)
    prev_scriptpubkey_b = getPrevScriptPubKey(tx, inp_index)
    isP2SH = False
    if checkWrappedP2WPKH(st) == True:
        prev_scriptpubkey_b = st[-1]
        st.pop()
        witness_l = getWitnessList(tx, inp_index)
        pushWitnessData(witness_l)
        print('P2SH_P2WPKH')
    if checkWrappedP2WSH(st) == True:
        prev_scriptpubkey_b = st[-1]
        st.pop()
        witness_l = getWitnessList(tx, inp_index)
        pushWitnessData(witness_l)
        print('P2SH_P2WSH')
    if checkWrappedMultisig(st) == True:
        redeemscript_b = st[-1]
        isP2SH = True
        print('P2SH')
    if isP2WPKH(prev_scriptpubkey_b) == True:
        print('P2WPKH')
        prev_scriptpubkey_b = bytes([0x76, 0xa9, 0x14]) + prev_scriptpubkey_b[2:] + bytes([0x88, 0xac])
    if isP2WSH(prev_scriptpubkey_b) == True:
        print('P2WSH')
        prev_scriptpubkey_b = bytes([0xa8, 0x20]) + prev_scriptpubkey_b[2:] + bytes([0x87])
    print('previous scriptpubkey = ', prev_scriptpubkey_b.hex())
    execScript(prev_scriptpubkey_b, inp_index, tx)
    status = st.pop()
    if status == b'\x01':
        print('1st Script succeeded')
    elif status == b'\x01':
        print('1st Script Failed')
        return
    else:
        print('1st Invalid state')
        return
    if isP2SH == True:
        execScript(redeemscript_b, inp_index, tx)
        status = st.pop()
        if status == b'\x01':
            print('2nd Script succeeded')
        elif status == b'\x01':
            print('2nd Script Failed')
        else:
            print('2nd Invalid state')
