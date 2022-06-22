import mmap
from CoinbaseTransaction import getCoinbaseTransactionInfo, getVarInt
from BlockTransactions import getTransactionInfo
from CalculateTransactionHash import getTransactionHash

if __name__ == '__main__': 
    # trimmed block for block hash 000000000000000082ccf8f1557c5d40b21edabb18d2d691cfbf87118bac7254 
    blk_b = bytes.fromhex('020000007ef055e1674d2e6551dba41cd214debbee34aeb544c7ec670000000000000000d3998963f80c5bab43fe8c26228e98d030edf4dcbe48a666f5c39e2d7a885c9102c86d536c890019593a470ded01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4803e09304062f503253482f0403c86d53087ceca141295a00002e522cfabe6d6d7561cf262313da1144026c8f7a43e3899c44f6145f39a36507d36679a8b7006104000000000000000000000001c8704095000000001976a91480ad90d403581fa3bf46086a91b2d9d4125db6c188ac0000000001000000014dff4050dcee16672e48d755c6dd25d324492b5ea306f85a3ab23b4df26e16e9000000008c493046022100cb6dc911ef0bae0ab0e6265a45f25e081fc7ea4975517c9f848f82bc2b80a909022100e30fb6bb4fb64f414c351ed3abaed7491b8f0b1b9bcd75286036df8bfabc3ea5014104b70574006425b61867d2cbb8de7c26095fbc00ba4041b061cf75b85699cb2b449c6758741f640adffa356406632610efb267cb1efa0442c207059dd7fd652eeaffffffff020049d971020000001976a91461cf5af7bb84348df3fd695672e53c7d5b3f3db988ac30601c0c060000001976a914fd4ed114ef85d350d6d40ed3f6dc23743f8f99c488ac00000000') 
    blk_m = mmap.mmap(-1, len(blk_b) + 1) 
    blk_m.write(blk_b) 
    blk_m.seek(80) 
    tx_cnt = getVarInt(blk_m) 
    coinbase_tx = getCoinbaseTransactionInfo(blk_m) 
    stb = blk_m.tell() 
    tx = getTransactionInfo(blk_m) 
    endb = blk_m.tell() 
    tx_hash = getTransactionHash(stb, endb, blk_b) 
    print('Transaction Hash = %s' % tx_hash) 
