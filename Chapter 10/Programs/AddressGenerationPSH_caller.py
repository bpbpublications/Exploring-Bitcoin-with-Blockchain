from AddressGenerationPKH import sh2address, hash160
from AddressGenerationPSH import createRedeemScript

if __name__ == '__main__':
    pubkey_l = ['037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7', '02fcb1c7507db15576ab35cd7c9b1ea570141a8b81c9938dae0320392b0f7034d0', '02d50250aa629914e3146a5123a362a516c8aa95e5f0a6f3a078bd31fabe383abc']
    redeem_script_b = createRedeemScript(pubkey_l, 2)
    print('redeem script = %s' % redeem_script_b.hex())
    sh = hash160(redeem_script_b)
    address = sh2address(sh)
    print('P2SH address = %s' % address)
