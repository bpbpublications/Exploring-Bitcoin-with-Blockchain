from FindTransactionInLevelDB import findTransaction, txindex_db_g
from VerifyScript_P2SH import verifyScript

if __name__ == '__main__':
    txid_s = '8b3e54e345d0b3e9278a27f1ab2aa2566aba8cbe7cf44b9aa1836c9d0fcc2625'
    inp_index = 0
    txid_b = bytes.fromhex(txid_s)[::-1]
    tx = findTransaction(txid_b, txindex_db_g)
    verifyScript(tx, inp_index)
