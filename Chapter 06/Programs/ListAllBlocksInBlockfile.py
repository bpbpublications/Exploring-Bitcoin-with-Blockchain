def parseSerialisedBlock(block_f): 
    serialized_blk = {} 
    serialized_blk['magic_num'] = block_f.read(4)[::-1].hex() 
    serialized_blk['blk_size'] = int.from_bytes(block_f.read(4), byteorder='little') 
    serialized_blk['version'] = block_f.read(4)[::-1].hex() 
    prev_blkhash_b = block_f.read(32) 
    serialized_blk['prev_blkhash'] = prev_blkhash_b[::-1].hex() 
    serialized_blk['merkle_root_hash'] = block_f.read(32)[::-1].hex() 
    serialized_blk['time'] = int.from_bytes(block_f.read(4), byteorder='little') 
    serialized_blk['bits'] = block_f.read(4)[::-1].hex() 
    serialized_blk['nonce'] = block_f.read(4)[::-1].hex() 
    return serialized_blk 
