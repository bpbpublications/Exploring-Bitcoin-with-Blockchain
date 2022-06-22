from PublicKey import privkeyWif2Hex, privkeyWif2pubkey

if __name__ == '__main__':
    privkey_wif = 'cNdY2QGfetwijtrqzCK5tAoc78NtGkQJ8smYVaugDW6puLXJvLZG'
    print('privkey(WIF) = ', privkey_wif)
    privkey_s, network, compress = privkeyWif2Hex(privkey_wif)
    pubkey_b = privkeyWif2pubkey(privkey_wif)
    print('pubkey = %s' % pubkey_b.hex())
    print('-------------------------------------------------------------')
    privkey_wif = '91phZVP8Q5yMLEZbD41vfnGYWwEZuxbjQ5huSxiPUkkTiQw8SL2'
    print('privkey(WIF) = ', privkey_wif)
    privkey_s, network, compress = privkeyWif2Hex(privkey_wif)
    pubkey_b = privkeyWif2pubkey(privkey_wif)
    print('pubkey = %s' % pubkey_b.hex())
