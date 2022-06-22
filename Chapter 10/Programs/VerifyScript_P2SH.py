from VerifyScript_P2PKH import getScriptSig, bytes2Mmap, decodePushdata, pushdata, getPrevScriptPubKey, st, opHash160, sigcheck

g_pushnumber = range(0x51, 0x61) # excludes 0x61

def opEqual():
    v1 = st.pop()
    v2 = st.pop()
    if v1 == v2:
        st.append(b'\x01')
    else:
        st.append(b'\x00')

def opNum(b: int):
    num = b - 0x50
    st.append(bytes([num]))

def opCheckMultisig(script_b: bytes, inp_index: int, tx: dict):
    pubkey_cnt = int.from_bytes(st.pop(), byteorder='little')
    pubkey_l = [st.pop() for i in range(pubkey_cnt)][::-1]
    sig_cnt = int.from_bytes(st.pop(), byteorder='little')
    sig_l = [st.pop() for i in range(sig_cnt)][::-1]
    sig_index = 0
    for pubkey_b in pubkey_l:
        v = sigcheck(sig_l[sig_index], pubkey_b, script_b, inp_index, tx)
        if v == b'\x01':
            sig_index += 1
            if sig_index == sig_cnt:
                break
    # convert True/False to b'\x01' or b'\x00'
    b = bytes([int(sig_index == sig_cnt and v == b'\x01')])
    st.append(b)

def checkWrappedMultisig(st): 
    script_b = st[-1] 
    val = script_b[-2] 
    if bytes([script_b[-1]]) == b'\xae' and val in g_pushnumber: 
        return True 
    else: 
        return False 

def execScript(script_b: bytes, inp_index: int, tx: dict): 
    l = len(script_b) 
    script_m = bytes2Mmap(script_b) 
    while script_m.tell() < l: 
        v = script_m.read(1) 
        b = int.from_bytes(v, byteorder='little') 
        if b == 0x00: 
            pass 
        elif b < 0x4f: 
            script_m.seek(-1, 1) 
            b = decodePushdata(script_m) 
            d = script_m.read(b) 
            pushdata(d) 
        elif v == b'\x76': 
            opDup() 
        elif v == b'\xa9': 
            opHash160() 
        elif b in g_pushnumber: 
            opNum(b) 
        elif v == b'\x87': 
            opEqual() 
        elif v == b'\x88': 
            opEqualVerify() 
        elif v == b'\xac': 
            opCheckSig(script_b, inp_index, tx) 
        elif v == b'\xae': 
            opCheckMultisig(script_b, inp_index, tx) 

def verifyScript(tx: dict, inp_index: int):
    maybeP2SH = False
    isP2SH = False
    scriptsig_b = getScriptSig(tx, inp_index)
    if scriptsig_b[0] == b'\x00':
        maybeP2SH = True
    execScript(scriptsig_b, inp_index, tx)
    prev_scriptpubkey_b = getPrevScriptPubKey(tx, inp_index)
    if checkWrappedMultisig(st) == True:
        redeemscript_b = st[-1]
        isP2SH = True
    execScript(prev_scriptpubkey_b, inp_index, tx)
    status = st.pop()
    if status == b'\x01':
        print('1st Script succeeded')
    elif status == b'\x01':
        print('1st Script Failed')
    else:
        print('1st Invalid state')
    if isP2SH == True:
        execScript(redeemscript_b, inp_index, tx)
        status = st.pop()
        if status == b'\x01':
            print('2nd Script succeeded')
        elif status == b'\x01':
            print('2nd Script Failed')
        else:
            print('2nd Invalid state')
