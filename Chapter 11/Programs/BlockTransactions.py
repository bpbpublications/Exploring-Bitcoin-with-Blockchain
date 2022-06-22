import mmap
from CoinbaseTransaction import getVarInt

def getTransactionInfo(blk_m: mmap):
    tx = {}
    tx['version'] = blk_m.read(4)[::-1].hex()
    tx['inp_cnt'] = getVarInt(blk_m)
    inp_l = []
    for i in range(tx['inp_cnt']):
        inp = {}
        inp['prev_tx_hash'] = blk_m.read(32)[::-1].hex()
        inp['prev_tx_out_index'] = int.from_bytes(blk_m.read(4), byteorder='little')
        inp['bytes_scriptsig'] = getVarInt(blk_m)
        inp['scriptsig'] = blk_m.read(inp['bytes_scriptsig']).hex()
        inp['sequence'] = int.from_bytes(blk_m.read(4), byteorder='little')
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
