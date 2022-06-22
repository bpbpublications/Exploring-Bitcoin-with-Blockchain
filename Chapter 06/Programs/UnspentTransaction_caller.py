from ChainstateIndex import chainstate_db_g
from UnspentTransaction import getUnspentTransactions

if __name__ == '__main__':
    tx = bytes.fromhex('a23203c053852755c97b87e354d1e9053a6d1a20d32892e8ee45dfa2c3105f94')[::-1]
    jsonobj = getUnspentTransactions(tx, 0, chainstate_db_g)
    print(jsonobj)
