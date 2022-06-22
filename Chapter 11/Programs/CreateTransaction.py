import mmap
import struct
from ecdsa import SigningKey, SECP256k1 
from ecdsa.util  import sigencode_der_canonize 
from PublicKey import base58checkDecode, privkeyWif2Hex, privkeyWif2pubkey
from PrivateKey import hash256
from ParseScript import OP_PUSHDATA1, OP_PUSHDATA2, OP_PUSHDATA4
from ParseScriptSig import SIGHASH_NONE, SIGHASH_SINGLE, SIGHASH_ALL, SIGHASH_ANYONECANPAY
from BlockTransactions import getTransactionInfo

OP_RETURN = 0x6a

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

def getSequence(txn_struct: dict, i: int):
    inp = txn_struct['inputs'][i]
    if 'sequence_type' in inp:
        if inp['sequence_type'] == 'time':
            sequence = inp['sequence'] | (1 << 22)
        else:
            sequence = inp['sequence']
        sequence_b = struct.pack('<L', sequence)
    else:
        if txn_struct['locktime'] > 0:
            # sequence
            sequence_b = bytes([0xfe, 0xff, 0xff, 0xff])
        else:
            # sequence
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

OP_2 = 0x52
OP_IF = 0x63
OP_ELSE = 0x67
OP_ENDIF = 0x68
OP_CHECKSEQUENCEVERIFY = 0xb2
OP_EQUALVERIFY = 0x88
OP_DROP = 0x75
OP_SHA256 = 0xa8
OP_CHECKSIG = 0xac

def createSignaturePreimage(txn_struct: dict,
                            script_b: bytes,
                            inp_index: int):
    preimage_b = b''
    preimage_b += struct.pack('<L', txn_struct['version'])
    hashtype = txn_struct['inputs'][inp_index]['hash_type']
    if hashtype & SIGHASH_ANYONECANPAY:
        preimage_b += createVarInt(1)
        inputs = [inp_index] # only current input is processed
    else:
        preimage_b += createVarInt(txn_struct['input_count'])
        inputs = range(txn_struct['input_count'])
    for i in inputs:
        inp = txn_struct['inputs'][i]
        preimage_b += bytes.fromhex(inp['prevtxn'])[::-1]
        preimage_b += struct.pack('<L', inp['prevtxnindex'])
        if i == inp_index:
            preimage_b += createVarInt(len(script_b))
            preimage_b += script_b
        else:
            preimage_b += b'\x00'
        preimage_b += getSequence(txn_struct, i)
    # remove SIGHASH_ANYONECANPAY
    if hashtype & 0x0F == SIGHASH_NONE:
        preimage_b += createVarInt(0)
    else:
        # remove SIGHASH_ANYONECANPAY
        if hashtype & 0x0F == SIGHASH_SINGLE:
            preimage_b += createVarInt(inp['input_index'] + 1)
            outputs = range(inp['input_index'] + 1)
        else:
            preimage_b += createVarInt(txn_struct['out_count'])
            outputs = range(txn_struct['out_count'])
        for out in outputs:
            outp = txn_struct['outputs'][out]
            if outp['script_type'] == '':
                preimage_b += bytes([0xff])*8
                preimage_b += bytes([0x00])
            else:
                preimage_b += struct.pack('<Q', outp['satoshis'])
                if outp['script_type'] == 'OP_RETURN':
                    content_b = bytes.fromhex(outp['content_hash256'])
                    scriptPubkey_b = bytes([OP_RETURN]) \
                                        + getWithPushdata(content_b)
                else:
                    scriptPubkey_b = \
                        getScriptPubkeyFromAddress(outp['address'])
                preimage_b += createVarInt(len(scriptPubkey_b))
                preimage_b += scriptPubkey_b
    preimage_b += struct.pack('<L', txn_struct['locktime'])
    preimage_b += struct.pack('<L', hashtype)
    return preimage_b

OP_FALSE = 0x00
OP_TRUE = 0x51

def createScriptSigForCond(signgrp: list,
                            script_b: bytes,
                            cond: bool):
    if cond:
        scriptSig_b = bytes([OP_0])
        for sign_b in signgrp:
            scriptSig_b += getWithPushdata(sign_b)
        scriptSig_b += bytes([OP_TRUE])
        scriptSig_b += getWithPushdata(script_b)
    else:
        scriptSig_b = encodePushdata(len(signgrp[0])) + signgrp[0]
        scriptSig_b += bytes([OP_FALSE])
        scriptSig_b += encodePushdata(len(script_b)) + script_b
    return scriptSig_b

def createScriptSigWithSecret(signgrp: list,
                                script_b: bytes,
                                secret: str,
                                cond: bool):
    if cond:
        scriptSig_b = getWithPushdata(signgrp[0])
        secret_b = secret.encode('utf-8')
        scriptSig_b += getWithPushdata(secret_b)
        scriptSig_b += bytes([OP_TRUE])
    else:
        scriptSig_b = getWithPushdata(signgrp[0])
        scriptSig_b += bytes([OP_FALSE])
    scriptSig_b += getWithPushdata(script_b)
    return scriptSig_b

def createScriptSigForRelTimeLock(signgrp: list,
                                    script_b: bytes):
    scriptSig_b = getWithPushdata(signgrp[0])
    scriptSig_b += getWithPushdata(script_b)
    return scriptSig_b

def signMessage(preimage_b: bytes, 
                privkey_wif: str, 
                hash_type: int): 
    hash_preimage = hash256(preimage_b) 
    privkey_s, network, compress = privkeyWif2Hex(privkey_wif) 
    if privkey_s.__len__() % 2 == 1: 
        privkey_s = "0{}".format(privkey_s) 
    if compress == True: 
        privkey_b = bytes.fromhex(privkey_s)[:-1] 
    else: 
        privkey_b = bytes.fromhex(privkey_s) 
    sk = SigningKey.from_string(privkey_b, curve=SECP256k1) 
    sig_b = sk.sign_digest(hash_preimage, 
                    sigencode=sigencode_der_canonize) \
                + bytes([hash_type]) 
    return sig_b 

def updateTxnStructInput(txn_struct: dict, index: int):
    txn_s = txn_struct['inputs'][index]['input_txn']
    txn_b = bytes.fromhex(txn_s)
    with mmap.mmap(-1, len(txn_b)) as txn_m:
        txn_m.write(txn_b)
        txn_m.seek(0)
        inp = getTransactionInfo(txn_m)
        txn_input = txn_struct['inputs'][index]
        txn_input['prevtxn'] = inp['inputs'][0]['prev_tx_hash']
        txn_input['prevtxnindex'] = inp['inputs'][0]['prev_tx_out_index']
        txn_input['scriptsig'] = inp['inputs'][0]['scriptsig']
    return txn_struct

def getSignaturesAndExecScripts(txn_struct: dict):
    signgrp_l = []
    script_l = []
    for inp_index in range(txn_struct['input_count']):
        inp = txn_struct['inputs'][inp_index]
        if 'input_txn' in inp:
            txn_struct = updateTxnStructInput(txn_struct, inp_index)
            signgrp_l.append([])
            script_l.append(b'')
        else:
            script_b = getExecutionScript(txn_struct, inp_index)
            preimage_b = createSignaturePreimage(txn_struct,
                                                script_b,
                                                inp_index)
            signgrp = []
            for privkey in inp['privkeys']:
                hashtype = inp['hash_type']
                sign_b = signMessage(preimage_b, privkey, hashtype)
                signgrp.append(sign_b)
            signgrp_l.append(signgrp)
            script_l.append(script_b)
    return txn_struct, signgrp_l, script_l

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
    if 'input_txn' in  txn_input: #added
        scriptSig = txn_input['scriptsig']
        scriptSig_b = bytes.fromhex(scriptSig)
    elif txn_input['script_type'] == 'P2SH_Multisig':
        scriptSig_b = createScriptSigForMultiSig(signgrp, script_b)
    elif txn_input['script_type'] == 'P2SH_RelativeTimeLock':
        scriptSig_b = createScriptSigForRelTimeLock(signgrp, script_b)
    elif txn_input['script_type'] == 'P2SH_Condition':
        scriptSig_b = createScriptSigForCond(signgrp,
                            script_b,
                            txn_input['condition'])
    elif txn_input['script_type'] == 'P2SH_WithSecret':
        if txn_input['condition']:
            scriptSig_b = createScriptSigWithSecret(signgrp,
                                script_b,
                                txn_input['secret'], True)
        else:
            scriptSig_b = createScriptSigWithSecret(signgrp,
                                script_b, '', False)
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
        sgntxn_b += getSequence(txn_struct, i)
    sgntxn_b += createVarInt(txn_struct['out_count'])
    for out in range(txn_struct['out_count']):
        outp = txn_struct['outputs'][out]
        if outp['script_type'] == '':
            sgntxn_b += bytes([0xff])*8
            sgntxn_b += bytes([0x00])
        else:
            sgntxn_b += struct.pack('<Q', outp['satoshis'])
            if outp['script_type'] == 'OP_RETURN':
                content_b = bytes.fromhex(outp['content_hash256'])
                scriptPubkey_b = bytes([OP_RETURN]) \
                                    + getWithPushdata(content_b)
            else:
                scriptPubkey_b =  \
                        getScriptPubkeyFromAddress(outp['address'])
            sgntxn_b += createVarInt(len(scriptPubkey_b))
            sgntxn_b += scriptPubkey_b
    sgntxn_b += struct.pack('<L', txn_struct['locktime'])
    return sgntxn_b
