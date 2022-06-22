import mmap
import os
from CoinbaseTransaction import getCoinbaseTransactionInfo, getVarInt
from BlockTransactions import getTransactionInfo
from BlockFileInfoFromBlockIndex import blocks_path_g
from TraverseBlockchain import getBlockIndex
from FindTransactionInLevelDB import findTransaction, BLOCK_HEADER_SIZE, txindex_db_g

def getTransactionOutAmount(tx_hash: bytes, out_index: int, txindex_db): 
    tx = findTransaction(tx_hash, txindex_db) 
    return tx['outs'][out_index]['satoshis']

def getTransactionFee(tx: dict):
    inp_val = 0
    for inp in tx['inputs']:
        prev_tx_hash = bytes.fromhex(inp['prev_tx_hash'])[::-1]
        inp_val += getTransactionOutAmount(prev_tx_hash, inp['prev_tx_out_index'], txindex_db_g)
    out_val = 0
    for out in tx['outs']:
        out_val += out['satoshis']
    tx_fee = inp_val - out_val
    return tx_fee

def getBlockFeeReward(block_hash: bytes, block_db):
    block_index = getBlockIndex(block_hash, block_db)
    if 'data_pos' in block_index:
        block_filepath = os.path.join(blocks_path_g, 'blk%05d.dat' % block_index['n_file'])
        start = block_index['data_pos']
    elif 'undo_pos' in block_index:
        block_filepath = os.path.join(blocks_path_g, 'rev%05d.dat' % block_index['n_file'])
        start = block_index['undo_pos']
    with open(block_filepath, 'r+b') as block_f:
        blk_m = mmap.mmap(block_f.fileno(), 0)
        blk_m.seek(start + BLOCK_HEADER_SIZE)
        tx_cnt = getVarInt(blk_m)
        print(tx_cnt)
        coinbase_tx = getCoinbaseTransactionInfo(blk_m)
        print(coinbase_tx)
        fee_reward = 0
        for i in range(1, tx_cnt):
            print(i)
            start = blk_m.tell()
            tx = getTransactionInfo(blk_m)
            end = blk_m.tell()
            tx_fee = getTransactionFee(tx)
            print(tx_fee)
            fee_reward += tx_fee
        return fee_reward
