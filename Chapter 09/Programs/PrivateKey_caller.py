from PrivateKey import encodeWifPrivkey

if __name__ == '__main__':
    h = 0x1f4b9c36e4f466464de890a341eba483eb3ed95932d797b0841afa1d8d83c420
    wif = encodeWifPrivkey(h, False)
    print(wif)
