import json
from FindTransactionInLevelDB import findTransaction, txindex_db_g

if __name__ == '__main__':
    tx_hash = bytes.fromhex('7301b595279ece985f0c415e420e425451fcf7f684fcce087ba14d10ffec1121')[::-1]
    tx = findTransaction(tx_hash, txindex_db_g)
    print("Transaction Info:\n", json.dumps(tx, indent = 4))
