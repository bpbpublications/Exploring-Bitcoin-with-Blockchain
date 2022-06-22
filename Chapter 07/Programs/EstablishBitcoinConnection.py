import socket
import hashlib
import datetime
import mmap
import ipaddress
from Utils import getVarInt, flog
from CreateMessage import createMessage
from CreateVersionPayload import createVersionPayload
from Utils import flog

def calculateChecksum(b: bytes):
    checksum = hashlib.sha256(hashlib.sha256(b).digest()).digest()[0:4]
    return checksum

def checkMessage(msghdr: dict, payload_b: bytes):
    if msghdr['magic'] == '0709110b':
        print('Magic check passed', file=flog)
    else:
        print('Magic check failed', file=flog)
        print('magic = %s' % msghdr['magic'], file=flog)
        raise Exception('Invalid Magic', file=flog)

    checksum_calc = calculateChecksum(payload_b)
    if msghdr['checksum'] == checksum_calc:
        print('checksum check passed', file=flog)
    else:
        print('checksum check failed', file=flog)
        print('payload = %s' % payload_b.hex(), file=flog)
        print('expected checksum = %s' % msghdr['checksum'].hex(), file=flog)
        print('received checksum = %s' % checksum_calc.hex(), file=flog)
        raise Exception('Invalid Checksum')

def parseMsgHdr(msghdr_b: bytes):
    msghdr = {}
    msghdr['magic'] = msghdr_b[0:4][::-1].hex()
    msghdr['command'] = msghdr_b[4:16].decode("ascii").strip('\0')
    msghdr['length'] = int.from_bytes(msghdr_b[16:20], byteorder='little')
    msghdr['checksum'] = msghdr_b[20:24]
    return msghdr

MSGHDR_SIZE = 24

def parseVersionPayload(payload_m: mmap, payloadlen: int):
    payload = {}
    start = payload_m.tell()
    payload['version'] = int.from_bytes(payload_m.read(4), byteorder='little')
    payload['services'] = int.from_bytes(payload_m.read(8), byteorder='little')
    parseServices(payload['services'])
    payload['timestamp'] = int.from_bytes(payload_m.read(8), byteorder='little')
    payload['dt'] = datetime.datetime.fromtimestamp(payload['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    payload['addr_recv'] = parseIPAddress(payload_m)
    payload['addr_trans'] = parseIPAddress(payload_m)
    payload['nonce'] = int.from_bytes(payload_m.read(8), byteorder='little')
    payload['user_agent_size'] = getVarInt(payload_m)
    payload['user_agent'] = payload_m.read(payload['user_agent_size'])
    payload['block_height'] = int.from_bytes(payload_m.read(4), byteorder='little')
    if payload_m.tell() - start != payloadlen:
        payload['relay'] = int.from_bytes(payload_m.read(1), byteorder='little')
    return payload

CMD_FN_MAP = {
    'version': parseVersionPayload,
#    'addr': parseAddrPayload,
#    'filterload': parseFilterLoadPayload,
#    'filteradd': parseFilterAddPayload,
#    'merkleblock': parseMerkleBlockPayload,
#    'ping': parsePingPongPayload,
#    'pong': parsePingPongPayload,
#    'feefilter': parseFeeFilterPayload,
#    'inv': parseInvPayload,
#    'getdata': parseInvPayload,
#    'notfound': parseInvPayload,
#    'tx': parseTxPayload,
#    'block': parseBlockPayload,
#    'getblocks': parseGetBlocksGetHeadersPayload,
#    'getheaders': parseGetBlocksGetHeadersPayload,
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

def parseIPAddress(ip_m: mmap):
    addr = {}
    addr['service'] = int.from_bytes(ip_m.read(8), byteorder='little')
    parseServices(addr['service'])
    ip = ip_m.read(16)
    if ip[0:12].hex() == "00000000000000000000ffff":
        addr['version'] = 'IPv4'
        addr['address'] = str(ipaddress.IPv4Address(ip[12:16]))
    else:
        addr['version'] = 'IPv6'
        addr['address'] = str(ipaddress.IPv6Address(ip[0:16]))
    addr['port'] = int.from_bytes(ip_m.read(2), byteorder='big')
    return addr

def parseServices(services: int):
    service_l = []
    if services == 0x00:
        service_l.append('Unnamed')
    if services & 0x01 == 0x01:
        service_l.append('NODE_NETWORK')
    if services & 0x02:
        service_l.append('NODE_GETUTXO')
    if services & 0x04:
        service_l.append('NODE_BLOOM')
    if services & 0x08:
        service_l.append('NODE_WITNESS')
    if services & 1024:
        service_l.append('NODE_NETWORK_LIMITED')
    print('Services: %d implies: %s' % (services, service_l), file=flog)

def sendVersionMessage(s: socket, version: int):
    sndcmd = 'version'
    payload = createVersionPayload(s, version)
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)
    return True

def waitForVersion(s: socket):
    recvmsg = recvMsg(s)
    vers_recvd = False
    if recvmsg['command'] != 'version':
        print('Invalid Response')
        return False
    services = recvmsg['payload']['services']
    if services & 1 == 0x00:
        print('Peer is not full node')
        return False
    return True

def sendVerackMessage(s: socket):
    sndcmd = 'verack'
    payload = b''
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)
    return True

def waitForVerack(s: socket):
    recvmsg = recvMsg(s)
    verack_recvd = False
    if recvmsg['command'] != 'verack':
        return False
    return True

def establishConnection(s: socket, version: int):
    vers_sent = sendVersionMessage(s, version)
    vers_recvd = waitForVersion(s)
    if vers_recvd == False:
        return False
    verack_sent = sendVerackMessage(s)
    verack_recvd = waitForVerack(s)
    if vers_sent and vers_recvd and verack_sent and verack_recvd:
        print('Connection is established', file=flog)
        return True
    return False
