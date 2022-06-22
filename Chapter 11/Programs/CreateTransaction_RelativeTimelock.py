from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts, OP_RETURN
from ParseScriptSig import SIGHASH_ALL

def createTransactionStruct():
    txn = {}
    txn['version'] = 2
    txn['input_count'] = 1
    txn['inputs'] = []
    input0 = {}
    input0['prevtxn'] = \
        'e6a31b5c7e39a31bb12c68055c1dd6dcb6554d1546a8621e889f1026e10264c8'
    input0['prevtxnindex'] = 0
    input0['script_type'] = 'P2SH_RelativeTimeLock'
    input0['privkeys'] = \
            ['L26JcHRhqEQv8V9DaAmE4bdszwqXS7tHznGYJPp7fxEoEQxxBPcQ']
    input0['redeem_script'] = '0169b27521037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7ac'
    input0['hash_type'] = SIGHASH_ALL
    input0['sequence'] = 105
    input0['sequence_type'] = 'block'
    txn['inputs'].append(input0)
    txn['out_count'] = 2
    txn['outputs'] = []
    output0 = {}
    output0['satoshis'] = 10*(10**8)
    output0['script_type'] = 'P2PKH'
    output0['address'] = 'mxzmMmVycLDgAA48VtHDeh389eDAwiJqwQ'
    txn['outputs'].append(output0)
    output1 = {}
    output1['satoshis'] = 399999*(10**4)
    output1['script_type'] = 'P2PKH'
    output1['address'] = 'miSFmBeKXf5Wp7Luj46XTu3Yh57nAwhZAo'
    txn['outputs'].append(output1)
    txn['locktime'] = 0
    return txn

if __name__ == '__main__':
    txn_struct = createTransactionStruct()
    txn_struct, signgrp_l, script_l = getSignaturesAndExecScripts(txn_struct)
    signed_txn_b = createSignedTransaction(txn_struct,
                                        signgrp_l,
                                        script_l)
    print(signed_txn_b.hex())
