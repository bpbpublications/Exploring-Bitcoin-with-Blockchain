import os
import plyvel
from B128VarInt import b128_varint_decode

block_db_g = plyvel.DB(os.getenv('BLOCK_INDEX_DB'), compression=None) 
blocks_path_g = os.getenv('BLOCKS_PATH') 

def getBlockFileIndex(n_file: int, block_db): 
    key = b'f' + (n_file).to_bytes(4, byteorder='little') 
    value = block_db.get(key) 
    jsonobj = {} 
    jsonobj['count'], pos = b128_varint_decode(value) 
    jsonobj['filesize'], pos = b128_varint_decode(value, pos) 
    jsonobj['undofilesize'], pos = b128_varint_decode(value, pos) 
    jsonobj['lowest'], pos = b128_varint_decode(value, pos) 
    jsonobj['highest'], pos = b128_varint_decode(value, pos) 
    jsonobj['lowest_timestamp'], pos = b128_varint_decode(value, pos) 
    jsonobj['highest_timestamp'], pos = b128_varint_decode(value, pos) 
    return jsonobj 
