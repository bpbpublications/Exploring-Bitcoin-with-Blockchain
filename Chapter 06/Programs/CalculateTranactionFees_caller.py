from BlockFileInfoFromBlockIndex import block_db_g
from CalculateTranactionFees import getBlockFeeReward

if __name__ == '__main__': 
    block_hash_b = bytes.fromhex('000000000000000004ec466ce4732fe6f1ed1cddc2ed4b328fff5224276e3f6f')[::-1] 
    total_tx_fee = getBlockFeeReward(block_hash_b, block_db_g) 
    print('Fee Reward = %d' % total_tx_fee) 
