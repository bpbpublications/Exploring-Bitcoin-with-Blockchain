import socket
import mmap
from Utils import getVarInt, flog
from CreateMessage import createMessage
from EstablishBitcoinConnection import parseIPAddress, \
                                checkMessage, \
                                parseVersionPayload, \
                                parseMsgHdr, \
                                establishConnection
from PingPong import createPongPayload

def parsePingPongPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['nonce'] = int.from_bytes(payload_m.read(8), byteorder='little')
    return payload

def parseAddrPayload(payload_m: mmap, payloadlen = 0): 
    payload = {} 
    payload['count'] = getVarInt(payload_m) 
    payload['addrs'] = [] 
    for i in range(payload['count']): 
        addr = {} 
        addr['timestamp'] = int.from_bytes(payload_m.read(4), byteorder='little') 
        addr['addr'] = parseIPAddress(payload_m) 
        payload['addrs'].append(addr) 
    return payload 

def parseGetBlocksGetHeadersPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['version'] = int.from_bytes(payload_m.read(4), byteorder='little')
    payload['hash count'] = getVarInt(payload_m)
    payload['block locator hashes'] = []
    for i in range(payload['hash count']):
        h = payload_m.read(32)[::-1].hex()
        payload['block locator hashes'].append(h)
    payload['hash_stop'] = payload_m.read(32)[::-1].hex()
    return payload

MSGHDR_SIZE = 24

CMD_FN_MAP = {
    'version': parseVersionPayload,
    'addr': parseAddrPayload,
#    'filterload': parseFilterLoadPayload,
#    'filteradd': parseFilterAddPayload,
#    'merkleblock': parseMerkleBlockPayload,
    'ping': parsePingPongPayload,
#    'pong': parsePingPongPayload,
#    'feefilter': parseFeeFilterPayload,
#    'inv': parseInvPayload,
#    'getdata': parseInvPayload,
#    'notfound': parseInvPayload,
#    'tx': parseTxPayload,
#    'block': parseBlockPayload,
    'getblocks': parseGetBlocksGetHeadersPayload,
    'getheaders': parseGetBlocksGetHeadersPayload,
#    'headers': parseHeadersPayload,
#    'reject': parseRejectPayload,
#    'sendcmpct': parseSendCompactPayload,
#    'cmpctblock': parseCompactBlockPayload,
#    'getblocktxn': parseGetBlockTxnPayload,
#    'blocktxn': parseBlockTxnPayload
}

def recvAll(s: socket, payloadlen: int):
    payload_b = b''
    length = payloadlen
    while True:
        recvd_b = s.recv(length)
        payload_b += recvd_b
        if len(payload_b) == payloadlen:
            break
        length = payloadlen - len(payload_b)
    return payload_b

def recvMsg(s: socket):
    global MSGHDR_SIZE, CMD_FN_MAP
    msghdr_b = s.recv(MSGHDR_SIZE)
    msg = parseMsgHdr(msghdr_b)
    payloadlen = msg['length']
    payload_b = recvAll(s, payloadlen)
    checkMessage(msg, payload_b)
    payload_m = mmap.mmap(-1, payloadlen + 1)
    payload_m.write(payload_b)
    payload_m.seek(0)
    msg['payload'] = {}
    if payloadlen > 0:
        msg['payload'] = CMD_FN_MAP[msg['command']](payload_m, payloadlen)
    print('<== msg = %s' % msg, file=flog)
    return msg

def sendrecvHandler(s: socket, version: int): 
    if establishConnection(s, version) == False: 
        print('Establish connection failed', file=flog) 
        return
    # send getaddr message 
    sndcmd = 'getaddr' 
    payload = b'' 
    sndmsg = createMessage(sndcmd, payload) 
    s.send(sndmsg) 
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog) 
    while True: 
        recvmsg = recvMsg(s) 
        if recvmsg['command'] == 'addr': 
            break 
        elif recvmsg['command'] == 'ping': 
            # send pong message 
            sndcmd = 'pong' 
            nonce = recvmsg['payload']['nonce'] 
            payload = createPongPayload(nonce) 
        elif recvmsg['command'] == 'getheaders': 
            # send header message 
            sndcmd = 'headers' 
            hashes = recvmsg['payload']['block locator hashes'] 
            stophash = recvmsg['payload']['hash_stop'] 
            payload = createHeadersPayload(hashes, stophash) 
        sndmsg = createMessage(sndcmd, payload) 
        s.send(sndmsg) 
        print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog) 
    if recvmsg['command'] == 'addr': 
        print('Received Addr', file=flog) 
