import mmap
from PrivateKey import hash256
from CoinbaseTransaction import getVarInt

def getTransactionInfo(txn_m: mmap): 
    tx = {} 
    startloc = txn_m.tell() 
    tx['version'] = txn_m.read(4)[::-1].hex() 
    tx['inp_cnt'] = getVarInt(txn_m) 
    tx['is_segwit'] = False 
    if tx['inp_cnt'] == 0: 
        # check segwit flag 
        tx['is_segwit'] = (int.from_bytes(txn_m.read(1), byteorder='little') == 1) 
        if tx['is_segwit'] == True: 
            tx['inp_cnt'] = getVarInt(txn_m) 
    inp_l = [] 
    for i in range(tx['inp_cnt']): 
        inp = {} 
        inp['prev_tx_hash'] = txn_m.read(32)[::-1].hex() 
#        inp['prev_tx_out_index'] = txn_m.read(4)[::-1].hex() 
        inp['prev_tx_out_index'] = int.from_bytes(txn_m.read(4), byteorder='little')
        inp['bytes_scriptsig'] = getVarInt(txn_m) 
        inp['scriptsig'] = txn_m.read(inp['bytes_scriptsig']).hex() 
#        inp['sequence'] = txn_m.read(4)[::-1].hex() 
        inp['sequence'] = int.from_bytes(txn_m.read(4), byteorder='little')
        inp_l.append(inp) 
    tx['inputs'] = inp_l 
    tx['out_cnt'] = getVarInt(txn_m) 
    out_l = [] 
    for i in range(tx['out_cnt']): 
        out = {} 
        out['satoshis'] = int.from_bytes(txn_m.read(8), byteorder='little') 
        out['bytes_scriptpubkey'] = getVarInt(txn_m) 
        out['scriptpubkey'] = txn_m.read(out['bytes_scriptpubkey']).hex() 
        out_l.append(out) 
    tx['outs'] = out_l 
    curloc = txn_m.tell() 
    txn_m.seek(startloc) 
    txid_b = txn_m.read(curloc - startloc) 
    if tx['is_segwit'] == True: 
        # if SegWit flag is true than remove SegWit marker and flag from txhash calculation 
        txid_b = txid_b[:4] + txid_b[6:] 
        for i in range(tx['inp_cnt']): 
            tx['inputs'][i]['witness_cnt'] = getVarInt(txn_m) 
            witness_l = [] 
            witness_cnt = tx['inputs'][i]['witness_cnt'] 
            for j in range(witness_cnt): 
                witness = {} 
                witness['size'] = getVarInt(txn_m) 
                witness['witness'] = txn_m.read(witness['size']).hex() 
                witness_l.append(witness) 
            tx['inputs'][i]['witnesses'] = witness_l 
    locktime_b = txn_m.read(4) 
    txid_b += locktime_b 
    tx['locktime'] = int.from_bytes(locktime_b, byteorder='little') 
    tx['txid'] = hash256(txid_b)[::-1].hex() 
    curloc = txn_m.tell() 
    txn_m.seek(startloc) 
    wtxid_b = txn_m.read(curloc - startloc) 
    tx['wtxid'] = hash256(wtxid_b)[::-1].hex() 
    tx['bytes'] = len(wtxid_b) 
    tx['weight'] = (len(wtxid_b) - len(txid_b)) + (len(txid_b) * 4) 
    return tx 
