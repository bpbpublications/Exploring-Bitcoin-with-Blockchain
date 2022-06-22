import bech32

witprog = bytes.fromhex('d0862d6e40d240ea1711f6d897f5e7b07e974a593704077edffb7b67fd34b091')
witver = 0x00
hrp = 'bc'
address = bech32.encode(hrp, witver, witprog)
print(address)
