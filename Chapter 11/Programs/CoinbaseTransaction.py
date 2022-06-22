import mmap 
import json 

def getVarInt(blk_m: mmap): 
    b_cnt_d = {'fd': 2, 'fe': 4, 'ff': 8} 
    prefix = int.from_bytes(blk_m.read(1), byteorder='little') 
    if prefix < 0xFD: 
        return prefix 
    else: 
        b_cnt = b_cnt_d['%x' % prefix] 
        size = int.from_bytes(blk_m.read(b_cnt), byteorder='little') 
        return size 

def getCoinbaseTransactionInfo(blk_m: mmap): 
    tx = {} 
    tx['version'] = blk_m.read(4)[::-1].hex() 
    tx['inp_cnt'] = getVarInt(blk_m) 
    inp_l = [] 
    for i in range(tx['inp_cnt']): 
        inp = {} 
        inp['prev_tx_hash'] = blk_m.read(32)[::-1].hex() 
        inp['prev_tx_out_index'] = int.from_bytes(blk_m.read(4), byteorder = 'little') 
        inp['bytes_coinbase_data'] = getVarInt(blk_m) 
        pos = blk_m.tell() 
        inp['bytes_height'] = getVarInt(blk_m) 
        inp['height'] = int.from_bytes(blk_m.read(inp['bytes_height']), byteorder='little') 
        size = blk_m.tell() - pos 
        coinbase_arb_data_size = inp['bytes_coinbase_data'] - size 
        inp['coinbase_arb_data'] = blk_m.read(coinbase_arb_data_size).hex() 
        inp['sequence'] = int.from_bytes(blk_m.read(4), byteorder = 'little') 
        inp_l.append(inp) 
    tx['inputs'] = inp_l 
    tx['out_cnt'] = getVarInt(blk_m) 
    out_l = [] 
    for i in range(tx['out_cnt']): 
        out = {} 
        out['satoshis'] = int.from_bytes(blk_m.read(8), byteorder='little') 
        out['bytes_scriptpubkey'] = getVarInt(blk_m) 
        out['scriptpubkey'] = blk_m.read(out['bytes_scriptpubkey']).hex() 
        out_l.append(out) 
    tx['outs'] = out_l 
    tx['locktime'] = int.from_bytes(blk_m.read(4), byteorder='little') 
    return tx 
