import hashlib
from AddressGenerationPKH import hash160, sh2address
from AddressSigWithSecret import createRedeemScriptWithSecretHash

if __name__ == '__main__':
    pubkey_agency = '037fadaea6edf196bf70af16cefb2bd3c830e54c0a6e9a00bf7806b241933547f7'
    pubkey_agent = '02fcb1c7507db15576ab35cd7c9b1ea570141a8b81c9938dae0320392b0f7034d0'
    secret = 'She sells seashells on the seashore'
    secret_h = hashlib.sha256(secret.encode('utf-8')).digest()
    redeem_script_b = createRedeemScriptWithSecretHash(pubkey_agency, pubkey_agent, secret_h)
    print('redeem script = %s' % redeem_script_b.hex())
    sh = hash160(redeem_script_b)
    address = sh2address(sh)
    print('P2SH address = %s' % address)
