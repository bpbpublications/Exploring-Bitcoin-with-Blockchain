import pbkdf2 
import hashlib 
import hmac 
import struct 
from cryptotools.ECDSA.secp256k1 import PublicKey, \
         PrivateKey, Point, G as secp256k1_G, \
         N as secp256k1_n, CURVE 
from PublicKey import privkeyHex2pubkey
from PrivateKey import base58checkEncode
from AddressGenerationPKH import hash160

iterations_g = 10000 
dklen_g = 64 # derived key length 

def genSeedFromStr(password: str, salt: str): 
    password_b = password.encode('utf-8') 
    salt_b = salt.encode('utf-8') 
    seed = pbkdf2.pbkdf2(hashlib.sha512, password_b, salt_b, iterations_g, dklen_g) 
    return seed 

def genMasterKeys(seed: bytes):
    h = hmac.new(bytes("Bitcoin seed", 'utf-8'),
                    seed,
                    hashlib.sha512).digest()
    private_key = int.from_bytes((h[0:32]), byteorder='big')
    chaincode = h[32:64]
    return private_key, chaincode

def finiteFieldAddition(a: int, b: int, modulo: int):
    return (a + b) % modulo

def genNormalChildPrivKey(privkey: int, chaincode: bytes, index: int):
    privkey_s = '%064x' % privkey
    pubkey_b = privkeyHex2pubkey(privkey_s, True)
    index_b = struct.pack('>L', index)
    h = hmac.new(chaincode, pubkey_b + index_b, 	                                             
                hashlib.sha512).digest()
    h256 = int.from_bytes(h[0:32], byteorder='big')
    child_privkey = finiteFieldAddition(h256, privkey, secp256k1_n)
    child_chaincode = h[32:64]
    return child_privkey, child_chaincode

G_p = Point(secp256k1_G[0], secp256k1_G[1])

def compressPubkey(pubkey_b: bytes):
    pubkey_P = PublicKey.decode(pubkey_b)
    pubkey_b = PublicKey.encode(pubkey_P, compressed=True)
    return pubkey_b

def genNormalChildPubKey(pubkey_b: bytes, chaincode: bytes, index: int):
    index_b = struct.pack('>L', index)
    h = hmac.new(chaincode, pubkey_b + index_b, hashlib.sha512).digest()
    h256 = int.from_bytes(h[0:32], byteorder='big')
    h256G = CURVE.point_mul(G_p, h256)
    pubkey_b = compressPubkey(pubkey_b)
    pubkey_point = Point.from_compact(pubkey_b[1:])
    child_pubkey_point = h256G + pubkey_point
    child_pubkey_b = PublicKey.encode(child_pubkey_point, compressed=True)
    child_chaincode = h[32:64]
    return child_pubkey_b, child_chaincode

def genNormalParentPrivKey(child_privkey_i: int,
                            pubkey_b: bytes,
                            chaincode: bytes,
                            index: int):
    index_b = struct.pack('>L', index)
    h = hmac.new(chaincode, pubkey_b + index_b, hashlib.sha512).digest()
    h256 = int.from_bytes(h[0:32], byteorder='big')
    privkey = finiteFieldAddition(-h256, child_privkey_i, secp256k1_n)
    return privkey

def genHardenedChildPrivKey(privkey: int, chaincode: bytes, index: int):
    index_b = struct.pack('>L', index)
    privkey_b = bytes.fromhex('%064x' % privkey)
    h = hmac.new(chaincode, b'\x00' + privkey_b + index_b, hashlib.sha512).digest()
    h256 = int.from_bytes(h[0:32], byteorder='big')
    child_privkey = finiteFieldAddition(h256, privkey, secp256k1_n)
    child_chaincode = h[32:64]
    return child_privkey, child_chaincode

XPUB_VERSION = '0488B21E' 
XPRV_VERSION = '0488ADE4' 
TPUB_VERSION = '043587CF' 
TPRV_VERSION = '04358394' 

def getMasterXPrv(chaincode_b: bytes, privkey: int): 
    version_b = bytes.fromhex(TPRV_VERSION) 
    depth_b = b'\x00' 
    fingerprint_p_b = bytes(4) 
    index_b = bytes(4) 
    privkey_b = bytes.fromhex('%066x' % privkey) 
    raw_xprv = depth_b + fingerprint_p_b + index_b + chaincode_b + privkey_b 
    xprv = base58checkEncode(version_b, raw_xprv) 
    return xprv 

def getMasterXPub(chaincode_b: bytes, pubkey: str): 
    version_b = bytes.fromhex(TPUB_VERSION) 
    depth_b = b'\x00' 
    fingerprint_p_b = bytes(4) 
    index_b = bytes(4) 
    pubkey_b = bytes.fromhex(pubkey) 
    raw_xpub = depth_b + fingerprint_p_b + index_b + chaincode_b + pubkey_b 
    xpub = base58checkEncode(version_b, raw_xpub) 
    return xpub 

def getXPrv(p_pubkey: str,
            chaincode_b: bytes,
            privkey: int,
            depth: int,
            index: int):
    version_b = bytes.fromhex(TPRV_VERSION)
    p_pubkey_b = bytes.fromhex(p_pubkey)
    privkey_b = bytes.fromhex('%066x' % privkey)
    depth_b = bytes([depth])
    p_fingerprint_b = hash160(p_pubkey_b)[0:4]
    index_b = struct.pack('>L', index)
    raw_xprv = depth_b + p_fingerprint_b + index_b + chaincode_b + privkey_b
    xprv = base58checkEncode(version_b, raw_xprv)
    return xprv

def getXPub(p_pubkey: str,
            chaincode_b: bytes,
            pubkey: str,
            depth: int,
            index: int):
    version_b = bytes.fromhex(TPUB_VERSION)
    p_pubkey_b = bytes.fromhex(p_pubkey)
    pubkey_b = bytes.fromhex(pubkey)
    depth_b = bytes([depth])
    p_fingerprint_b = hash160(p_pubkey_b)[0:4]
    index_b = struct.pack('>L', index)
    raw_xpub = depth_b + p_fingerprint_b + index_b + chaincode_b + pubkey_b
    xpub = base58checkEncode(version_b, raw_xpub)
    return xpub
