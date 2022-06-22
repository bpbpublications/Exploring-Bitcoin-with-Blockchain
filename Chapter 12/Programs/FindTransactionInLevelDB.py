import os
import json
import mmap
import plyvel
from B128VarInt import b128_varint_decode
from BlockFileInfoFromBlockIndex import blocks_path_g
from SegwitBlockTransaction import getTransactionInfo 

txindex_db_g = plyvel.DB(os.getenv('TX_INDEX_DB'), compression=None) 
BLOCK_HEADER_SIZE = 80 

def getTransactionIndex(tx_hash: bytes, txindex_db): 
    key = b't' + tx_hash 
    value = txindex_db.get(key) 
    jsonobj = {} 
    jsonobj['n_file'], pos = b128_varint_decode(value) 
    jsonobj['block_offset'], pos = b128_varint_decode(value, pos) 
    jsonobj['file_offset'], pos = b128_varint_decode(value, pos) 
    print(jsonobj) 
    return jsonobj 

def findTransaction(tx_hash: bytes, txindex_db): 
    jsonobj = getTransactionIndex(tx_hash, txindex_db) 
    print('Transaction Index:') 
    print(json.dumps(jsonobj, indent=4)) 
    block_filepath = os.path.join(blocks_path_g, 'blk%05d.dat' % jsonobj['n_file'])
    with open(block_filepath, 'r+b') as blk_f: 
        blk_m = mmap.mmap(blk_f.fileno(), 0) # map whole file 
        blk_m.seek(jsonobj['block_offset'] + BLOCK_HEADER_SIZE + jsonobj['file_offset']) 
        tx = getTransactionInfo(blk_m) 
        blk_m.close() 
        return tx 
