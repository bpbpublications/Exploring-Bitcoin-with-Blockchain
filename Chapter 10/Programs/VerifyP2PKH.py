from VerifyScript_P2PKH import verifyScript
from FindTransactionInLevelDB import findTransaction, txindex_db_g

if __name__ == '__main__':
    txid_s = '2df97b379c9ce9e4a60529f555b9742c04f90b922c2fcff846ebae41206b93f9'
    inp_index = 1
    txid_b = bytes.fromhex(txid_s)[::-1]
    tx = findTransaction(txid_b, txindex_db_g)
    verifyScript(tx, inp_index)
