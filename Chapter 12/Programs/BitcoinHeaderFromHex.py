def getBlockHeader(blk: bytes): 
    block = {} 
    block['version'] = blk[0:4][::-1].hex() 
    blk = blk[4:] 
    block['prev_blockhash'] = blk[0:32][::-1].hex() 
    blk = blk[32:] 
    block['merkle_root'] = blk[0:32][::-1].hex() 
    blk = blk[32:] 
    block['time'] =int.from_bytes(blk[0:4], byteorder='little') 
    blk = blk[4:] 
    block['bits'] = blk[0:4][::-1].hex() 
    blk = blk[4:] 
    block['nonce'] = blk[0:4][::-1].hex() 
    return block 

