from AddressGenerationPKH import pubkey2address

if __name__ == '__main__':
    pubkey = '0281238fc6d981efce6aa1b3ccb8556a1b115a40f8ab3315c003f415ceedc3defe'
    pubkey_b = bytes.fromhex(pubkey)
    print('Compressed PubKey = ', pubkey_b.hex())
    address = pubkey2address(pubkey_b)
    print('Address = ', address)
    print('-----------------------------------------------')
    pubkey = '0440bb63da114aa89f4d2cf35d695d3e52e6add7a4bae06f190d947bef5c62b5e0e99601851593a9e54e2059a25d76512698acf60089935dedc015f1bb2bc81eda'
    pubkey_b = bytes.fromhex(pubkey)
    print('Uncompressed PubKey = ', pubkey_b.hex())
    address = pubkey2address(pubkey_b)
    print('Address = ', address)
