import hashlib
from CreateTransaction import createSignedTransaction, getSignaturesAndExecScripts, OP_RETURN
from ParseScriptSig import SIGHASH_ALL

story = '''Best Friend Lunch Party: One day two best friends, a monkey and a crocodile decided to have lunch together in a farm. The next day they passed the river and reached the farm. After a heavy meal the monkey got up and started growling loudly. The frightened crocodile pleaded the monkey to stop. But the monkey said, 'I have a habit of growling after every meal, I cannot help it'. The monkey was on the crocodiles back while crossing the river back home. When they were halfway through the river, the crocodile took a dip in the water. When the monkey was frightened, the crocodile said, 'I have a habit of taking a dip in the water after every meal, I cannot help it'. Monkey understood his mistake.'''

def contentHash(story: str):
    content_h = hashlib.sha256(story.encode('ascii')).digest()
    return content_h

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
    input0['hash_type'] = SIGHASH_ALL
    txn['inputs'].append(input0)
    txn['out_count'] = 2
    txn['outputs'] = []
    output0 = {}
    output0['satoshis'] = 4999900000
    output0['script_type'] = 'P2PKH'
    output0['address'] = 'mxzmMmVycLDgAA48VtHDeh389eDAwiJqwQ'
    txn['outputs'].append(output0)
    output1 = {}
    output1['satoshis'] = 0
    output1['script_type'] = 'OP_RETURN'
#    output1['content_hash256'] = '3365b392ee14def189190638a532f6042446b74c98f186e9b595f77e47817e05'
    output1['content_hash256'] = contentHash(story).hex()
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
