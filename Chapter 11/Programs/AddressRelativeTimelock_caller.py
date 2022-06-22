from AddressRelativeTimelock import createRedeemScript
from AddressGenerationPKH import hash160, sh2address

if __name__ == '__main__':
    pubkey_alice = '037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7'
    redeem_script_b = createRedeemScript(pubkey_alice)
    print('redeem script = %s' % redeem_script_b.hex())
    sh = hash160(redeem_script_b)
    address = sh2address(sh)
    print('P2SH address = %s' % address)
