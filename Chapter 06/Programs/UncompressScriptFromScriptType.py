def uncompressScriptType0(script_data: bytes): 
    script = bytes([ 
            0x76, # OP_DUP 
            0xa9, # OP_HASH160 
            20 # size 
            ]) + script_data + bytes([ 
            0x88, # OP_EQUALVERIFY 
            0xac # OP_CHECKSIG 
            ]) 
    return script 
