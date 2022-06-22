import hashlib
from PrivateKey import base58checkEncode

PKH_MAINNET_PREFIX = 0x00 
SH_MAINNET_PREFIX = 0x05 
PKH_TESTNET_PREFIX = 0x6F 
SH_TESTNET_PREFIX = 0xC4 
PKH_REGTEST_PREFIX = 0x6F 
SH_REGTEST_PREFIX = 0xC4 

def hash160(secret: bytes): 
    secrethash = hashlib.sha256(secret).digest() 
    h = hashlib.new('ripemd160') 
    h.update(secrethash) 
    secret_hash160 = h.digest() 
    return secret_hash160 

def hash256(bstr: bytes): 
    return hashlib.sha256(hashlib.sha256(bstr).digest()).digest() 

def pkh2address(pkh: bytes): 
    prefix = PKH_TESTNET_PREFIX 
    address = base58checkEncode(bytes.fromhex('%02x' % prefix), pkh) 
    return address 

def sh2address(sh: bytes): 
    prefix = SH_TESTNET_PREFIX 
    address = base58checkEncode(bytes.fromhex('%02x' % prefix), sh)
    return address 

def pubkey2address(pubkey: bytes): 
    pkh = hash160(pubkey) 
    address = pkh2address(pkh) 
    return address 
