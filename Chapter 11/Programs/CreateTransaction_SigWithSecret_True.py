from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts
from ParseScriptSig import SIGHASH_ALL

def createTransactionStruct():
    txn = {}
    txn['version'] = 1
    txn['input_count'] = 1
    txn['inputs'] = []
    input0 = {}
    input0['prevtxn'] = \
        '5bdcb4a0ff46b4443cfa1ff8002a8ccff06e56a8100a259fbfbd4b0ab660d481'
    input0['prevtxnindex'] = 0
    input0['script_type'] = 'P2SH_WithSecret'
    input0['privkeys'] = \
             ['KxR8HHyfAwFPidCw2vXThXqT4vSMNeufirHFapnfCfkzLaohtujG']
    input0['redeem_script'] = '63a82009b5eb7277b9d5062d91fe20f141ad4dd81970fd0baa72d31ee346a7c48d5b8c882102fcb1c7507db15576ab35cd7c9b1ea570141a8b81c9938dae0320392b0f7034d0ac670169b27521037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7ac68'
    input0['secret'] = 'She sells seashells on the seashore'
    input0['condition'] = True
    input0['hash_type'] = SIGHASH_ALL
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
    txn['locktime'] = 0 # block height
    return txn

if __name__ == '__main__':
    txn_struct = createTransactionStruct()
    txn_struct, signgrp_l, script_l = getSignaturesAndExecScripts(txn_struct)
    signed_txn_b = createSignedTransaction(txn_struct,
                                        signgrp_l,
                                        script_l)
    print(signed_txn_b.hex())
