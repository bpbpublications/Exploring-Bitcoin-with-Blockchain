from B128VarInt import b128_varint_encode, b128_varint_decode

if __name__ == '__main__':
    for num in [127, 128, 255, 256, 16383, 16384, 16511, 64535, 65535, 2**32]:
        enc = b128_varint_encode(num)
        print("num = %d, enc = %s, dec = %d" % (num, enc.hex(), b128_varint_decode(enc)[0]))
