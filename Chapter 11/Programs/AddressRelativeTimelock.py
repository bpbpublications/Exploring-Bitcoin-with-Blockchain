from CreateTransaction import OP_CHECKSEQUENCEVERIFY, OP_CHECKSIG, OP_DROP, createVarInt

def createRedeemScript(pubkey_alice: str): 
    redeem_script_b = bytes([0x01, 
                            105, # after 105 blocks 
                            OP_CHECKSEQUENCEVERIFY, OP_DROP]) 
    pubkey_b = bytes.fromhex(pubkey_alice) 
    redeem_script_b += createVarInt(len(pubkey_b)) + pubkey_b 
    redeem_script_b += bytes([OP_CHECKSIG]) 
    return redeem_script_b 
