from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts
from ParseScriptSig import SIGHASH_ANYONECANPAY, SIGHASH_NONE, SIGHASH_ALL

def createTransactionStruct(): 
    txn = {} 
    txn['version'] = 1 
    txn['input_count'] = 3 
    txn['inputs'] = [] 
    input0 = {} 
    input0['input_txn'] = '01000000018f99caaceba9a1b3890b34e7a6565c8c3dfb593a5b4f89c4b961f0324ef0fc5e000000006a4730440220591f7386623f53235ad7f7f6df87caa060067e29e158b54e7248fa036de6630602207fdd8f364c7a3576ba3b2c9e3df7bab5a4122b56e5fec7a4582377d2f8d0e1f082210281238fc6d981efce6aa1b3ccb8556a1b115a40f8ab3315c003f415ceedc3defeffffffff0000000000' 
    input0['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_NONE 
    txn['inputs'].append(input0) 
    input1 = {} 
    input1['input_txn'] = '01000000012fc10012a63217aa0636628381d92bdb9b94ff847b1cb2ddb51fee8ae0c69579000000006b483045022100d6ab49ea6ce096738036b38b30532a5ca17a51755a7b81e661506223eb16ec3c022071a10e3069aea32cf23f4f27b043850f7fcf656424b5724680ad1a5cc9a6ca998221037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7ffffffff0000000000' 
    input1['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_NONE 
    txn['inputs'].append(input1) 
    input2 = {} 
    input2['prevtxn'] = 'c83e8dc76b2139f84235d38907291ebe2470786b2d5977302a63aff1c5d99649' 
    input2['prevtxnindex'] = 0 
    input2['script_type'] = 'P2PKH' 
    input2['privkeys'] = ['KxR8HHyfAwFPidCw2vXThXqT4vSMNeufirHFapnfCfkzLaohtujG'] 
    input2['script_pubkey'] = '76a9142004e0ff6a6f08115d048fd9af177fae702f681a88ac' 
    input2['hash_type'] = SIGHASH_ALL 
    txn['inputs'].append(input2) 
    txn['out_count'] = 2 
    txn['outputs'] = [] 
    output0 = {} 
    output0['satoshis'] = 12500000000 
    output0['script_type'] = 'P2PKH' 
    output0['address'] = 'mnhWcUMqe9J1G4t3NMqNmLUqxfPTgwv7NK' 
    txn['outputs'].append(output0) 
    output1 = {} 
    output1['satoshis'] = 2499900000 
    output1['script_type'] = 'P2PKH' 
    output1['address'] = 'mtRkMmpT6uhM9LXVPRk4ck9Gcaz9iuQgmZ' 
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
