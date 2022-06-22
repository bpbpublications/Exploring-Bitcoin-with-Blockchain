import struct
from ecdsa import SigningKey, SECP256k1 
from ecdsa.util  import sigencode_der_canonize 
from PublicKey import base58checkDecode, privkeyWif2Hex, privkeyWif2pubkey
from PrivateKey import hash256
from ParseScript import OP_PUSHDATA1, OP_PUSHDATA2, OP_PUSHDATA4

def getExecutionScript(txn_struct: dict, inp_index: int): 
    inp = txn_struct['inputs'][inp_index] 
    script_type = inp['script_type'] 
    if script_type[:4] == 'P2SH': 
        script_b = bytes.fromhex(inp['redeem_script']) 
    elif script_type == 'P2PKH': 
        script_b = bytes.fromhex(inp['script_pubkey']) 
    return script_b 

def getScriptPubkeyP2PKH(address: str):
    pkh_b = address2PubkeyHash(address)
    pkhSize_b = encodePushdata(len(pkh_b))
    scriptPubkey_b = bytes([OP_DUP, OP_HASH160]) \
                        + pkhSize_b + pkh_b \
                        + bytes([OP_EQUALVERIFY]) \
                        + bytes([OP_CHECKSIG])
    return scriptPubkey_b

def getScriptPubkeyP2SH(address: str):
    sh_b = address2PubkeyHash(address)
    shSize_b = encodePushdata(len(sh_b))
    scriptPubkey_b = bytes([OP_HASH160]) \
                    + shSize_b \
                    + sh_b \
                    + bytes([OP_EQUAL])
    return scriptPubkey_b

def getScriptPubkeyFromAddress(address: str):
    pkh_b = address2PubkeyHash(address)
    pkhSize_b = encodePushdata(len(pkh_b))
    script_type = getScriptTypeFromAddress(address)
    if script_type == 'P2PKH':
        scriptPubkey_b = getScriptPubkeyP2PKH(address)
    elif script_type == 'P2SH':
        scriptPubkey_b = getScriptPubkeyP2SH(address)
    return scriptPubkey_b

def getSequence(txn_struct: dict): 
    if txn_struct['locktime'] > 0: 
        sequence_b = bytes([0xfe, 0xff, 0xff, 0xff]) 
    else: 
        sequence_b = bytes([0xff, 0xff, 0xff, 0xff]) 
    return sequence_b 

def createVarInt(i: int): 
    if i < 0xfd: 
        return bytes([i]) 
    elif i < 0xffff: 
        return b'\xfd' + struct.pack('<H', i) 
    elif i < 0xffffffff: 
        return b'\xfe' + struct.pack('<L', i) 
    elif i < 0xffffffffffffffff: 
        return b'\xff' + struct.pack('<Q', i) 

def address2PubkeyHash(address: str): 
    pkh = base58checkDecode(address) 
    return pkh 

def encodePushdata(length: int): 
    if length <= 0x4b: 
        return bytes([length]) 
    if length <= 0xff: 
        return bytes([OP_PUSHDATA1, length]) 
    if length <= 0xffff: 
        return bytes([OP_PUSHDATA2]) + struct.pack('<H', length) 
    if length <= 0xffffffff: 
        return bytes([OP_PUSHDATA4]) + struct.pack('<L', length) 

def getScriptTypeFromAddress(address: str): 
    if address[0] in ['m', 'n'] or address[0] == '1': 
        return "P2PKH" 
    elif address[0] == '2' or address[0] == '3': 
        return "P2SH" 

OP_0 = 0x00 
OP_DUP = 0x76 
OP_EQUAL = 0x87 
OP_EQUALVERIFY = 0x88 
OP_HASH160 = 0xa9 
OP_CHECKSIG = 0xac 
OP_CHECKMULTISIG = 0xae 

def createSignaturePreimage(txn_struct: dict,
                            script_b: bytes,
                            inp_index: int):
    preimage_b = b''
    preimage_b += struct.pack('<L', txn_struct['version'])
    preimage_b += createVarInt(txn_struct['input_count'])
    for i in range(txn_struct['input_count']):
        inp = txn_struct['inputs'][i]
        preimage_b += bytes.fromhex(inp['prevtxn'])[::-1]
        preimage_b += struct.pack('<L', inp['prevtxnindex'])
        if i == inp_index:
            preimage_b += createVarInt(len(script_b))
            preimage_b += script_b
        else:
            preimage_b += b'\x00'
        preimage_b += getSequence(txn_struct)
    preimage_b += createVarInt(txn_struct['out_count'])
    for out in range(txn_struct['out_count']):
        satoshis = txn_struct['outputs'][out]['satoshis']
        preimage_b += struct.pack('<Q', satoshis)
        address = txn_struct['outputs'][out]['address']
        scriptPubkey_b = getScriptPubkeyFromAddress(address)
        preimage_b += createVarInt(len(scriptPubkey_b))
        preimage_b += scriptPubkey_b
    preimage_b += struct.pack('<L', txn_struct['locktime'])
    hashtype = txn_struct['inputs'][inp_index]['hash_type']
    preimage_b += struct.pack('<L', hashtype)
    print('preimage = ', preimage_b.hex())
    return preimage_b

def signMessage(preimage_b: bytes, 
                privkey_wif: str, 
                hash_type: int): 
    hash_preimage = hash256(preimage_b) 
    privkey_s, network, compress = privkeyWif2Hex(privkey_wif) 
    print(privkey_s, network, compress)
    if privkey_s.__len__() % 2 == 1: 
        privkey_s = "0{}".format(privkey_s) 
    if compress == True: 
        print('compress is true') 
        privkey_b = bytes.fromhex(privkey_s)[:-1] 
    else: 
        privkey_b = bytes.fromhex(privkey_s) 
    sk = SigningKey.from_string(privkey_b, curve=SECP256k1) 
    sig_b = sk.sign_digest(hash_preimage, 
                    sigencode=sigencode_der_canonize) \
                + bytes([hash_type]) 
    return sig_b 

def getSignaturesAndExecScripts(txn_struct: dict): 
    signgrp_l = [] 
    script_l = [] 
    for inp_index in range(txn_struct['input_count']): 
        inp = txn_struct['inputs'][inp_index] 
        script_b = getExecutionScript(txn_struct, inp_index) 
        preimage_b = createSignaturePreimage(txn_struct, 
                                            script_b, 
                                            inp_index) 
        inp = txn_struct['inputs'][inp_index] 
        signgrp = [] 
        for privkey in inp['privkeys']: 
            hashtype = inp['hash_type'] 
            sign_b = signMessage(preimage_b, privkey, hashtype) 
            signgrp.append(sign_b) 
        signgrp_l.append(signgrp) 
        script_l.append(script_b) 
    return signgrp_l, script_l 

def getWithPushdata(data_b: bytes):
    pushdata_b = encodePushdata(len(data_b))
    return pushdata_b + data_b

def createScriptSigForMultiSig(signgrp: list, script_b: bytes):
    scriptSig_b = bytes([OP_0])
    for sign_b in signgrp:
        scriptSig_b += getWithPushdata(sign_b)
    scriptSig_b += getWithPushdata(script_b)
    return scriptSig_b

def createScriptSigForP2PKH(txn_input: dict, signgrp: list):
    sign_b = signgrp[0] # it's not a group.. just one signature
    scriptSig_b = getWithPushdata(sign_b)
    privkey = txn_input['privkeys'][0]
    pubkey_b = privkeyWif2pubkey(privkey)
    scriptSig_b += getWithPushdata(pubkey_b)
    return scriptSig_b

def createSignedInput(txn_input: dict,
                        signgrp,
                        script_b: bytes):
    prevtxn = txn_input['prevtxn']
    prevtx_rb = bytes.fromhex(prevtxn)[::-1]
    prevtxnindex = txn_input['prevtxnindex']
    sgntxnin_b = prevtx_rb + struct.pack('<L', prevtxnindex)
    if txn_input['script_type'] == 'P2SH_Multisig':
        scriptSig_b = createScriptSigForMultiSig(signgrp, script_b)
    elif txn_input['script_type'] == 'P2PKH':
        scriptSig_b = createScriptSigForP2PKH(txn_input, signgrp)
    sgntxnin_b += createVarInt(len(scriptSig_b)) + scriptSig_b
    return sgntxnin_b

# In P2PKH script scriptSig is signature + pubkey
def scriptSigFromSignNPubkey(sign_b: bytes, pubkey_b: bytes):
    scriptSig_b = getWithPushdata(sign_b)
    scriptSig_b += getWithPushdata(pubkey_b)
    return scriptSig_b

def createSignedTransaction(txn_struct: dict,
                            signgrp_l: list,
                            script_l: list):
    sgntxn_b = b''
    sgntxn_b += struct.pack('<L', txn_struct['version'])
    sgntxn_b += createVarInt(txn_struct['input_count'])
    for i in range(txn_struct['input_count']):
        txn_input = txn_struct['inputs'][i]
        sgntxn_b += createSignedInput(txn_input,
                                        signgrp_l[i],
                                        script_l[i])
        sgntxn_b += getSequence(txn_struct)
    sgntxn_b += createVarInt(txn_struct['out_count'])
    for out in range(txn_struct['out_count']):
        satoshis = txn_struct['outputs'][out]['satoshis']
        sgntxn_b += struct.pack('<Q', satoshis)
        address = txn_struct['outputs'][out]['address']
        scriptPubkey_b = getScriptPubkeyFromAddress(address)
        sgntxn_b += createVarInt(len(scriptPubkey_b))
        sgntxn_b += scriptPubkey_b
    sgntxn_b += struct.pack('<L', txn_struct['locktime'])
    return sgntxn_b
