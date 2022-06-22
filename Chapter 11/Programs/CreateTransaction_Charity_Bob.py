from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts
from ParseScriptSig import SIGHASH_ANYONECANPAY, SIGHASH_NONE

def createTransactionStruct():
    txn = {}
    txn['version'] = 1
    txn['input_count'] = 1
    txn['inputs'] = []
    input0 = {}
    input0['prevtxn']='7995c6e08aee1fb5ddb21c7b84ff949bdb2bd98183623606aa1732a61200c12f' 
    input0['prevtxnindex'] = 0
    input0['script_type'] = 'P2PKH'
    input0['privkeys'] = ['L26JcHRhqEQv8V9DaAmE4bdszwqXS7tHznGYJPp7fxEoEQxxBPcQ'] 
    input0['script_pubkey'] = '76a914db610ec1429ecb422044ee4ea92f11bc080fdb3d88ac' 
    input0['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_NONE
    txn['inputs'].append(input0)
    txn['out_count'] = 0
    txn['locktime'] = 0
    return txn

if __name__ == '__main__':
    txn_struct = createTransactionStruct()
    txn_struct, signgrp_l, script_l = getSignaturesAndExecScripts(txn_struct)
    signed_txn_b = createSignedTransaction(txn_struct,
                                        signgrp_l,
                                        script_l)
    print(signed_txn_b.hex())
