from CreateTransaction import encodePushdata

OP_CHECKMULTISIG = 0xae 

def createRedeemScript(pubkey_l: list, sigcount: int): 
    redeem_script_b = bytes([0x50 + sigcount]) 
    for pubkey in pubkey_l: 
        pubkey_b = bytes.fromhex(pubkey) 
        redeem_script_b += encodePushdata(len(pubkey_b)) + pubkey_b 
    redeem_script_b += bytes([0x50 + len(pubkey_l), OP_CHECKMULTISIG]) 
    return redeem_script_b 
