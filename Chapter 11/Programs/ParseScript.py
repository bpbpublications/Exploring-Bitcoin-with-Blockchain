op_d = {'76': 'OP_DUP', 'a9': 'OP_HASH160', '88': 'OP_EQUALVERIFY', '87': 'OP_EQUAL', 'ac': 'OP_CHECKSIG', 'ae': 'OP_CHECKMULTISIG', '00': 'OP_0', '51': 'OP_1', '52': 'OP_2', '53': 'OP_3', '54': 'OP_4', '55': 'OP_5', '56': 'OP_6', '57': 'OP_7', '58': 'OP_8', '59': 'OP_9', '5a': 'OP_10', '5b': 'OP_11', '5c': 'OP_12', '5d': 'OP_13', '5e': 'OP_14', '5f': 'OP_15', '60': 'OP_16', '6a': 'OP_RETURN', '4c': 'OP_PUSHDATA1', '4d': 'OP_PUSHDATA2', '4e': 'OP_PUSHDATA4'} 

OP_PUSHDATA1 = 0x4c 
OP_PUSHDATA2 = 0x4d 
OP_PUSHDATA4 = 0x4e 

g_pushdata = range(0x01, 0x4c) 

def prepare_readable_script(script_b: bytes): 
    script_len = len(script_b) 
    script_sl = [] 
    i = 0 
    while i < script_len: 
        if script_b[i] in g_pushdata: 
            script_sl.append(script_b[i: i + 1].hex()) 
            script_sl.append(script_b[i+1: i+script_b[i]+1].hex()) 
            i += 1 + script_b[i] 
        elif script_b[i] == OP_PUSHDATA1: 
            script_sl.append(op_d[script_b[i:i+1].hex()]) 
            datasize_b = script_b[i + 1: i + 2] 
            script_sl.append(datasize_b.hex()) 
            datasize = int.from_bytes(datasize_b, byteorder='little') 
            script_sl.append(script_b[i + 2: i + 2 + datasize].hex()) 
            i += 2 + datasize 
        elif script_b[i] == OP_PUSHDATA2: 
            script_sl.append(op_d[script_b[i:i+1].hex()]) 
            datasize_b = script_b[i + 1: i + 3] 
            script_sl.append(datasize_b.hex()) 
            datasize = int.from_bytes(datasize_b, byteorder='little') 
            script_sl.append(script_b[i + 3: i + 3 + datasize].hex()) 
            i += 3 + datasize 
        elif script_b[i] == OP_PUSHDATA4: 
            script_sl.append(op_d[script_b[i:i+1].hex()]) 
            datasize_b = script_b[i + 1: i + 5] 
            script_sl.append(datasize_b.hex()) 
            datasize = int.from_bytes(datasize_b, byteorder='little') 
            script_sl.append(script_b[i + 5: i + 5 + datasize].hex()) 
            i += 5 + data_size 
        else: 
            op_s = op_d[script_b[i:i+1].hex()] 
            script_sl.append(op_s) 
            i += 1 
    script_str = ' '.join(script_sl) 
    return script_str 
