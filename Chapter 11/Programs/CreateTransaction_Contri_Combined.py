from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts
from ParseScriptSig import SIGHASH_ANYONECANPAY, SIGHASH_ALL

def createTransactionStruct(): 
    txn = {} 
    txn['version'] = 1 
    txn['input_count'] = 3 
    txn['inputs'] = [] 
    input0 = {} 
    input0['input_txn'] = '01000000018f99caaceba9a1b3890b34e7a6565c8c3dfb593a5b4f89c4b961f0324ef0fc5e000000006b483045022100c74f16f961f0dfc3f60a27ff38a863a37ae22c06b385820ac7bac16dfd65c2970220026ee8509c7fe18f1c35c37d42dcc1dfcf7ffdf30418895c0baf77616e0c029a81210281238fc6d981efce6aa1b3ccb8556a1b115a40f8ab3315c003f415ceedc3defeffffffff01f0ae117e030000001976a9148343cfe3998d8a49bcfeea63dcbe12643a8e884788ac00000000'
    input0['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_ALL 
    txn['inputs'].append(input0) 
    input1 = {} 
    input1['input_txn'] = '01000000012fc10012a63217aa0636628381d92bdb9b94ff847b1cb2ddb51fee8ae0c69579000000006b483045022100e802af3b669187b65a7f10184e3924240cba9d322f6949e909590d8f5465bc59022014e1ed26198b744d91a51fadc7255172bc75e771cbf4b1a968b1d62d9a03adf68121037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7ffffffff01f0ae117e030000001976a9148343cfe3998d8a49bcfeea63dcbe12643a8e884788ac00000000' 
    input1['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_ALL 
    txn['inputs'].append(input1) 
    input2 = {} 
    input2['prevtxn'] = 'c83e8dc76b2139f84235d38907291ebe2470786b2d5977302a63aff1c5d99649' 
    input2['prevtxnindex'] = 0 
    input2['script_type'] = 'P2PKH' 
    input2['privkeys'] = ['KxR8HHyfAwFPidCw2vXThXqT4vSMNeufirHFapnfCfkzLaohtujG'] 
    input2['script_pubkey'] = '76a9142004e0ff6a6f08115d048fd9af177fae702f681a88ac' 
    input2['hash_type'] = SIGHASH_ALL 
    txn['inputs'].append(input2) 
    txn['out_count'] = 1 
    txn['outputs'] = [] 
    output0 = {} 
    output0['satoshis'] = 14999990000 
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

