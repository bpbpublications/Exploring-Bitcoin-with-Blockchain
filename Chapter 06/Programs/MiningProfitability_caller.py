from TraverseBlockchain import getBlockIndex
from BitcoinHeaderFromHex import getBlockHeader
from CalculateBlockReward import getBlockReward
from BlockFileInfoFromBlockIndex import block_db_g
from MiningProfitability import miningReturn, getBlockHeaderBytes, MINER_POWER_WATT, MINER_HASH_RATE

if __name__ == '__main__': 
    blk_hash = bytes.fromhex('000000000000000000079dc864537510659e14439ff5f4a208231bcf276358ba')[::-1] 
    blk_index = getBlockIndex(blk_hash, block_db_g) 
    blk_hdr_b = getBlockHeaderBytes(blk_hash) 
    jsonobj = getBlockHeader(blk_hdr_b) 
    blk_reward = getBlockReward(blk_index['height']) 
    bits_b = bytes.fromhex(jsonobj['bits'])[::-1] 
    mining_return = miningReturn(MINER_POWER_WATT, MINER_HASH_RATE, bits_b, blk_reward) 
    print("Mining Return Per Month = %s" % (mining_return)) 
