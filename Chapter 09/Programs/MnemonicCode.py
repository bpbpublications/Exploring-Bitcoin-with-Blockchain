import hashlib
import random
import math

def getChecksumBitCount(mnemonic_length: int): 
    if (mnemonic_length % 3) != 0: 
            raise ValueError('Invalid Mnemonic code length') 
    checksum_bit_count = mnemonic_length // 3 
    return checksum_bit_count 

def getEntropyBitCount(mnemonic_length: int): 
    if (mnemonic_length % 3) != 0: 
        raise ValueError('Invalid Mnemonic code length') 
    entropy_bit_count = (mnemonic_length * 32) // 3 
    return entropy_bit_count 

def getRandomNumberBits(bit_count: int):
    r = random.SystemRandom().randrange(0, 1 << 32)
    r_b = r.to_bytes((r.bit_length() + 7) // 8, 'big')
    h = hashlib.sha256()
    h.update(r_b)
    h_b = h.digest()
    byte_count = bit_count // 8
    rand_num_b = h_b[0:byte_count]
    return rand_num_b

def getMSBChecksumBits(checksum: int, checksum_bit_count: int):
    msb_checksum = checksum >> (256 - checksum_bit_count)
    return msb_checksum

def getEntropyWithChecksum(random_number: int,
                            msb_checksum: int,
                            checksum_bit_count: int):
    shifted_random_number = random_number << checksum_bit_count
    entropy_check_i = shifted_random_number | msb_checksum
    return entropy_check_i

def convertIntToBytes(num: int, bit_count: int):
    size_bytes = math.ceil(bit_count / 8)
    num_s = ('%x' % num).zfill(size_bytes * 2)
    num_b = bytes.fromhex(num_s)
    return num_b

def getChecksum(b: bytes):
    return int.from_bytes(hashlib.sha256(b).digest(), byteorder='big')

def getEntropyCheckBits(mnemonic_length: int):
    entropy_bit_count = getEntropyBitCount(mnemonic_length)
    random_number_b = getRandomNumberBits(entropy_bit_count)
    checksum_bit_count = getChecksumBitCount(mnemonic_length)
    checksum = getChecksum(random_number_b)
    msb_checksum = getMSBChecksumBits(checksum, checksum_bit_count)
    random_number = int.from_bytes(random_number_b, byteorder='big')
    entropy_check_i = getEntropyWithChecksum(random_number, msb_checksum,
                                                checksum_bit_count)
    bit_count = entropy_bit_count + checksum_bit_count
    entropy_check_b = convertIntToBytes(entropy_check_i, bit_count)
    return entropy_check_b

def getMnemonicWordList():
    word_list = []
    with open('mnemonic_word_list_english.txt', 'rt') as word_file:
            word_list = word_file.read().splitlines()
    return word_list

def entropyCheckBits2List(entropy_check_b: bytes, size: int):
    selector_int = int.from_bytes(entropy_check_b, byteorder='big')
    selector_list = []
    while size >= 11:
        selector_list.append(selector_int & 0x07FF)
        selector_int = selector_int >> 11
        size -= 11
    return selector_list[::-1]

def getMnemonicWordCodeString(mnemonic_length: int):
    entropy_bit_count = getEntropyBitCount(mnemonic_length)
    checksum_bit_count = getChecksumBitCount(mnemonic_length)
    entropy_check_bit_count = entropy_bit_count + checksum_bit_count
    entropy_check_b = getEntropyCheckBits(mnemonic_length)
    selector_list = entropyCheckBits2List(entropy_check_b,
                            entropy_check_bit_count)
    mnemonic_word_list = getMnemonicWordList()
    word_key_list = []
    for selector in selector_list:
        word = mnemonic_word_list[selector]
        word_key_list.append(word)
    return word_key_list
