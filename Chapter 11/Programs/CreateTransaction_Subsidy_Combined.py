from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts
from ParseScriptSig import SIGHASH_ANYONECANPAY, SIGHASH_SINGLE, SIGHASH_ALL

def createTransactionStruct(): 
    txn = {} 
    txn['version'] = 1 
    txn['input_count'] = 3 
    txn['inputs'] = [] 
    input0 = {} 
    input0['input_txn'] = '01000000018f99caaceba9a1b3890b34e7a6565c8c3dfb593a5b4f89c4b961f0324ef0fc5e000000006b483045022100d02ff4c770f95de80b4bada8d301c6cc98fcd22c4b5436783e44eb069bb3301702201921d63c42d554ebede3dc649bddf56279d41388b50af0056c1c2a6e33cb16ff83210281238fc6d981efce6aa1b3ccb8556a1b115a40f8ab3315c003f415ceedc3defeffffffff01c058628d010000001976a9148343cfe3998d8a49bcfeea63dcbe12643a8e884788ac00000000' 
    input0['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_SINGLE 
    txn['inputs'].append(input0) 
    input1 = {} 
    input1['input_txn'] = '01000000012fc10012a63217aa0636628381d92bdb9b94ff847b1cb2ddb51fee8ae0c69579000000006b483045022100d8995b5289e2852932e667ce77b937cf7c1d440e6148bd1590aa3cf776710f98022030320cb072787f2c15bd9449ce6d352178a44a8c42d47ead8e70d87895ab2eb68321037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7ffffffff02ffffffffffffffff00c058628d010000001976a9144ec804774aba76cb4685b5152d6924d8ce5c87ae88ac00000000'
    input1['hash_type'] = SIGHASH_ANYONECANPAY|SIGHASH_SINGLE 
    txn['inputs'].append(input1) 
    input2 = {} 
    input2['prevtxn'] = 'c83e8dc76b2139f84235d38907291ebe2470786b2d5977302a63aff1c5d99649' 
    input2['prevtxnindex'] = 0 
    input2['script_type'] = 'P2PKH' 
    input2['privkeys'] = ['KxR8HHyfAwFPidCw2vXThXqT4vSMNeufirHFapnfCfkzLaohtujG'] 
    input2['script_pubkey'] = '76a9142004e0ff6a6f08115d048fd9af177fae702f681a88ac' 
    input2['hash_type'] = SIGHASH_ALL 
    txn['inputs'].append(input2) 
    txn['out_count'] = 3 
    txn['outputs'] = [] 
    output0 = {} 
    output0['satoshis'] = 6667000000 
    output0['script_type'] = 'P2PKH' 
    output0['address'] = 'msV23rBcHAtQWSkWV9ph91DV65VduWi1Vt' 
    txn['outputs'].append(output0) 
    output1 = {} 
    output1['satoshis'] = 6667000000 
    output1['script_type'] = 'P2PKH' 
    output1['address'] = 'mnhWcUMqe9J1G4t3NMqNmLUqxfPTgwv7NK' 
    txn['outputs'].append(output1) 
    output2 = {} 
    output2['satoshis'] = 1665990000 
    output2['script_type'] = 'P2PKH' 
    output2['address'] = 'mtRkMmpT6uhM9LXVPRk4ck9Gcaz9iuQgmZ' 
    txn['outputs'].append(output2) 
    txn['locktime'] = 0 
    return txn 

if __name__ == '__main__':
    txn_struct = createTransactionStruct()
    txn_struct, signgrp_l, script_l = getSignaturesAndExecScripts(txn_struct)
    signed_txn_b = createSignedTransaction(txn_struct,
                                        signgrp_l,
                                        script_l)
    print(signed_txn_b.hex())
