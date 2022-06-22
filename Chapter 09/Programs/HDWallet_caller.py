from PrivateKey import encodeWifPrivkey, encodeWifPrivkey
from PublicKey import privkeyHex2pubkey
from HDWallet import genSeedFromStr, genMasterKeys, \
        genNormalChildPrivKey, genNormalChildPubKey, \
        genNormalParentPrivKey, genHardenedChildPrivKey, \
        getMasterXPrv, getMasterXPub, getXPrv, getXPub

if __name__ == '__main__': 
    mnemonic_code_l = ['moral', 'submit', 'comfort', 'cupboard', 'organ', 
            'expand', 'home', 'bid', 'dawn', 'ozone', 'omit', 'helmet'] 
    mnemonic_code = ' '.join(mnemonic_code_l) 
    print('Mnemonic Code = ', mnemonic_code) 
    seed = genSeedFromStr(mnemonic_code, 'mnemonic' + 'mycomplexpasscode') 
    print('seed = %s' % seed.hex()) 

    privkey, chaincode = genMasterKeys(seed) 
    privkey_s = '%064x' % privkey 
    print('master privkey = %s' % privkey_s) 
    print('master chaincode = %s' % chaincode.hex()) 

    child_privkey_i, child_chaincode = genNormalChildPrivKey(privkey, chaincode, 1) 
    child_privkey_wif = encodeWifPrivkey(child_privkey_i, True) 
    print("child privkey = %s" % child_privkey_wif) 
    print("child chaincode = %s" % child_chaincode.hex()) 

    pubkey_b = privkeyHex2pubkey(privkey_s, True) 
    child_pubkey_b, child_chaincode = genNormalChildPubKey(pubkey_b, chaincode, 1) 
    print("child pubkey key = %s" % child_pubkey_b.hex()) 
    print("child chaincode = %s"% child_chaincode.hex()) 

    p_privkey_i = genNormalParentPrivKey(child_privkey_i,  
                                        pubkey_b, chaincode, 1) 
    p_privkey_wif = encodeWifPrivkey(p_privkey_i, True) 
    print('parent privkey = %064x' % p_privkey_i) 

    index = ((1<<31) + 1) # 2^31 + 1 
    child_privkey_i, child_chaincode = genHardenedChildPrivKey(privkey, chaincode, index) 
    child_privkey_wif = encodeWifPrivkey(child_privkey_i, True) 
    print("child privkey = %s" % child_privkey_wif) 
    print("child chaincode = %s" % child_chaincode.hex()) 

    xprv = getMasterXPrv(chaincode, privkey) 
    print('xprv=%s' % xprv) 
    pubkey_b = privkeyHex2pubkey(privkey_s, True) 
    xpub = getMasterXPub(chaincode, pubkey_b.hex()) 
    print('xprv=%s' % xpub) 

    # We are calculating for index=1 and depth=1 
    child_xprv = getXPrv(pubkey_b.hex(), child_chaincode, child_privkey_i, 1, 1) 
    print('child xprv:') 
    print(child_xprv) 

    child_xpub = getXPub(pubkey_b.hex(), child_chaincode, child_pubkey_b.hex(),1, 1) 
    print('child xpub:') 
    print(child_xpub) 
