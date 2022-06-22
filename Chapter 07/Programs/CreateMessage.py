import hashlib
import struct

def createMessage(command, payload): 
    magic = 0x0709110B 
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[0:4] 
    magic_b = struct.pack('<L', magic) 
    cmd_b = struct.pack('<12s', command.encode('ascii')) 
    payload_len_b = struct.pack('<L', len(payload)) 
    checksum_b = struct.pack('<4s', checksum) 
    msg = magic_b + cmd_b + payload_len_b + checksum + payload 
    return msg 
