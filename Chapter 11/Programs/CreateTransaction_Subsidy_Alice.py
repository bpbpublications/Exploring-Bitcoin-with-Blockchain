from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts
from ParseScriptSig import SIGHASH_ANYONECANPAY, SIGHASH_SINGLE

def createTransactionStruct(): 
    txn = {} 
    txn['version'] = 1 
    txn['input_count'] = 1 
    txn['inputs'] = [] 
    input0 = {} 
    input0['prevtxn'] = '5efcf04e32f061b9c4894f5b3a59fb3d8c5c56a6e7340b89b3a1a9ebacca998f' 
    input0['prevtxnindex'] = 0 
    input0['script_type'] = 'P2PKH' 
    input0['privkeys'] = ['KwfxnwxpPG1RmhU8jaU8Ron4m1KZGymLAFNaMnSTonoZ7AQfnV53'] 
    input0['script_pubkey'] = '76a91481d7033c19dcec645cb3f86ce41678756850ba4d88ac' 
    input0['input_index'] = 0 
    input0['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_SINGLE 
    txn['inputs'].append(input0) 
    txn['out_count'] = 1 
    txn['outputs'] = [] 
    output0 = {} 
    output0['satoshis'] = 6667000000 
    output0['script_type'] = 'P2PKH' 
    output0['address'] = 'msV23rBcHAtQWSkWV9ph91DV65VduWi1Vt' 
    txn['outputs'].append(output0) 
    txn['locktime'] = 0 
    return txn 

if __name__ == '__main__':
    txn_struct = createTransactionStruct()
    txn_struct, signgrp_l, script_l = getSignaturesAndExecScripts(txn_struct)
    signed_txn_b = createSignedTransaction(txn_struct,
                                        signgrp_l,
                                        script_l)
    print(signed_txn_b.hex())
