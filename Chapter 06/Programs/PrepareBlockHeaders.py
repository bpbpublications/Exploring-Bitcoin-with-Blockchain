from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('test', 'test'))

def getRawTransaction(txid: str): 
    rawtx = rpc_connection.getrawtransaction(txid) 
    return rawtx 

def getVersionBytes(supported_softfork_bits: int):
    version = 0x20000000 | supported_softfork_bits
    v_bytes = bytes.fromhex(hex(version))[::-1]
    return v_bytes

def getTimeBytes():
    t = time.time()
    time_b = bytes.fromhex(hex(t))[::-1]
    return time_b

def calculateNextTargetThreshold(): 
    block_hash = rpc_connection.getblockhash(height) 
    block = rpc_connection.getblock(block_hash, 0) 
    blkhdr = getBlockHeader(bytes.fromhex(block)) 
    bits = bytes.fromhex(blkhdr['bits'])[::-1] 
    tt_old = getTargetThreshold(bits) 
    block_hash_2015 = rpc_connection.getblockhash(height-2015) 
    block_2015 = rpc_connection.getblock(block_hash_2015, 0) 
    blkhdr_2015 = getBlockHeader(bytes.fromhex(block_2015)) 
    delta_t = blkhdr['time'] - blkhdr_2015['time'] 
    tt_new = tt_old * (blkhdr['time'] - blkhdr_2015['time'])//(2016 * 600) 
    return tt_new 

def targetThreshold2bits(tt: int): 
    tt_b = tt.to_bytes((tt.bit_length() + 7) // 8, 'big') 
    print(tt_b.hex()) 
    prepend = b"0" if tt_b[0] > 0x7f else b"" 
    tt_b = prepend + tt_b 
    b1 = bytes([len(tt_b)]) 
    tt_b = tt_b + bytes(2) 
    tt_b = tt_b[0:3] 
    bits = b1 + tt_b 
    return bits 

def getBits():
    if height % 2016 != 0:
        block_hash = rpc_connection.getblockhash(height)
        blkhdr = getBlockHeader(bytes.fromhex(block))
        return bytes.fromhex(blkhdr['bits'])[::-1]
    tt = calculateNextTargetThreshold()
    bits = targetThreshold2bits(tt)
    return bits
