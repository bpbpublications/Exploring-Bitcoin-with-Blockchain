from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts
from ParseScriptSig import SIGHASH_ALL

def createTransactionStruct(): 
    txn = {} 
    txn['version'] = 1 
    txn['input_count'] = 2 
    txn['inputs'] = [] 
    input0 = {} 
    input0['prevtxn'] = \
        '5efcf04e32f061b9c4894f5b3a59fb3d8c5c56a6e7340b89b3a1a9ebacca998f' 
    input0['prevtxnindex'] = 0 
    input0['script_type'] = 'P2PKH' 
    input0['privkeys'] = ['KwfxnwxpPG1RmhU8jaU8Ron4m1KZGymLAFNaMnSTonoZ7AQfnV53'] 
    input0['script_pubkey'] = '76a91481d7033c19dcec645cb3f86ce41678756850ba4d88ac' 
    input0['hash_type'] = SIGHASH_ALL 
    txn['inputs'].append(input0) 
    input1 = {} 
    input1['prevtxn'] = '53793974d074e57305575d711fd0acd1d39f406264de234e686542ad2d0ddbfb' 
    input1['prevtxnindex'] = 0 
    input1['script_type'] = 'P2PKH' 
    input1['privkeys'] = ['KwfxnwxpPG1RmhU8jaU8Ron4m1KZGymLAFNaMnSTonoZ7AQfnV53'] 
    input1['script_pubkey'] = '76a91481d7033c19dcec645cb3f86ce41678756850ba4d88ac' 
    input1['hash_type'] = SIGHASH_ALL 
    txn['inputs'].append(input1) 
    txn['out_count'] = 2 
    txn['outputs'] = [] 
    output0 = {} 
    output0['satoshis'] = 40*(10**8) 
    output0['script_type'] = 'P2PKH' 
    output0['address'] = 'mxzmMmVycLDgAA48VtHDeh389eDAwiJqwQ' 
    txn['outputs'].append(output0) 
    output1 = {} 
    output1['satoshis'] = 599999*(10**4) 
    output1['script_type'] = 'P2PKH' 
    output1['address'] = 'miSFmBeKXf5Wp7Luj46XTu3Yh57nAwhZAo' 
    txn['outputs'].append(output1) 
    txn['locktime'] = 110 # block height 
    return txn 

#if __name__ == '__main__':
#    txn_struct = createTransactionStruct()
#    scriptSig_l = getScriptSigs(txn_struct)
#    signed_txn_b = createSignedTransaction(txn_struct, scriptSig_l)
#    print(signed_txn_b.hex())
if __name__ == '__main__':
    txn_struct = createTransactionStruct()
    signgrp_l, script_l = getSignaturesAndExecScripts(txn_struct)
    signed_txn_b = createSignedTransaction(txn_struct,
                                        signgrp_l,
                                        script_l)
    print(signed_txn_b.hex())
