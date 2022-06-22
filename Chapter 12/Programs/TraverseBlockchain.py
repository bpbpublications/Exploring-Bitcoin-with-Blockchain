import os
import datetime
import pandas as pd
import mmap
from B128VarInt import b128_varint_decode
from BlockFileInfoFromBlockIndex import block_db_g, blocks_path_g
from ChainstateIndex import getRecentBlockHash, chainstate_db_g

BLOCK_HAVE_DATA = 8 
BLOCK_HAVE_UNDO = 16 

def getBlockIndex(block_hash_b: bytes, block_db): 
    key = b'b' + block_hash_b 
    value = block_db.get(key) 
    jsonobj = {} 
    jsonobj['version'], pos = b128_varint_decode(value) 
    jsonobj['height'], pos = b128_varint_decode(value, pos) 
    jsonobj['status'], pos = b128_varint_decode(value, pos) 
    jsonobj['tx_count'], pos = b128_varint_decode(value, pos) 
    if jsonobj['status'] & (BLOCK_HAVE_DATA | BLOCK_HAVE_UNDO): 
            jsonobj['n_file'], pos = b128_varint_decode(value, pos) 
    if jsonobj['status'] & BLOCK_HAVE_DATA: 
            jsonobj['data_pos'], pos = b128_varint_decode(value, pos) 
    if jsonobj['status'] & BLOCK_HAVE_UNDO: 
            jsonobj['undo_pos'], pos = b128_varint_decode(value, pos) 
    jsonobj['header'] = {} 
    jsonobj['header']['version'] = value[pos:pos+4][::-1].hex() 
    jsonobj['header']['prevblockhash'] = value[pos+4:pos+36][::-1].hex() 
    jsonobj['header']['merkleroot'] = value[pos+36:pos+68][::-1].hex() 
    jsonobj['header']['time'] = value[pos+68:pos+72][::-1].hex() 
    jsonobj['header']['bits'] = value[pos+72:pos+76][::-1].hex() 
    jsonobj['header']['nonce'] = value[pos+76:pos+80][::-1].hex() 
    return jsonobj 

def getTransactionCount(mptr: mmap):
    prefix = int.from_bytes(mptr.read(1), byteorder='little')
    b_cnt_m = {'fd': 2, 'fe': 4, 'ff': 8}
    if prefix < 0xFD:
        tx_cnt = prefix
    else:
        b_cnt = b_cnt_m['%x' % prefix]
        tx_cnt = int.from_bytes(mptr.read(b_cnt), byteorder='little')
    return tx_cnt

def parseBlockHeader(mptr: mmap, start: int, height: int):
    seek = start-8
    mptr.seek(seek)
    block_header = {}
    block_header['magic_number'] = int.from_bytes(mptr.read(4), byteorder='little')
    block_header['block_size'] = int.from_bytes(mptr.read(4), byteorder='little')
    block_header['version'] = int.from_bytes(mptr.read(4), byteorder='little')
    prev_block_header_hash = mptr.read(32)
    block_header['prev_block_hash'] = prev_block_header_hash[::-1].hex()
    block_header['merkle_tree_root'] = mptr.read(32)[::-1].hex()
    block_header['timestamp'] = int.from_bytes(mptr.read(4), byteorder='little')
    block_header['date_time'] = datetime.datetime.fromtimestamp(block_header['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
#    block_header['bits'] = int.from_bytes(mptr.read(4), byteorder='little')
    block_header['bits'] = mptr.read(4)[::-1].hex()
#    block_header['nonce'] = int.from_bytes(mptr.read(4), byteorder='little')
    block_header['nonce'] = mptr.read(4)[::-1].hex()
    txcount = getTransactionCount(mptr)
    return block_header, prev_block_header_hash

#def parseBlockHeader(mptr: mmap, start: int, height: int):
#    ret = False
#    seek = start-4
#    mptr.seek(seek)
#    block_header = {}
#    block_header['block_size'] = int(binascii.hexlify(mptr.read(4)[::-1]), 16)
#    v_b = mptr.read(4)
#    block_header['version'] = int(binascii.hexlify(v_b[::-1]), 16)
#    prev_block_header_hash = mptr.read(32)
#    block_header['prev_block_hash'] = bytes.decode(binascii.hexlify(prev_block_header_hash[::-1]))
#    block_header['merkle_tree_root'] = bytes.decode(binascii.hexlify(mptr.read(32)[::-1]))
#    block_header['timestamp'] = int(binascii.hexlify(mptr.read(4)[::-1]), 16)
#    block_header['date_time'] = datetime.datetime.fromtimestamp(block_header['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
#    block_header['bits'] = bytes.decode(binascii.hexlify(mptr.read(4)[::-1]))
#    block_header['nounce'] = bytes.decode(binascii.hexlify(mptr.read(4)[::-1]))

def traverseBlockChain():
    df = pd.DataFrame()
    prev_blockhash_bigendian_b = getRecentBlockHash(chainstate_db_g)
    blockheader_list = []
    while True:
        jsonobj = getBlockIndex(prev_blockhash_bigendian_b, block_db_g)
        print(jsonobj['n_file'])
        if 'data_pos' in jsonobj:
            block_filepath = os.path.join(blocks_path_g, 'blk%05d.dat' % jsonobj['n_file'])
            start = jsonobj['data_pos']
            print('height = %d' % jsonobj['height'])
        elif 'undo_pos' in jsonobj:
            block_filepath = os.path.join(blocks_path_g, 'rev%05d.dat' % jsonobj['n_file'])
            start = jsonobj['undo_pos']
        # load file to memory
        with open(block_filepath, 'rb') as block_file:
            with mmap.mmap(block_file.fileno(), 0, prot = mmap.PROT_READ, flags = mmap.MAP_PRIVATE) as mptr: #File is open read-only
                blockheader, prev_blockhash_bigendian_b = parseBlockHeader(mptr, start, jsonobj['height'])
        blockheader['height'] = jsonobj['height']
        blockheader['tx_count'] = jsonobj['tx_count']
        blockheader_list.append(blockheader)
        if jsonobj['height'] == 1:
            break
    df = pd.DataFrame(blockheader_list)
    df.to_csv('out.csv', index=False)
