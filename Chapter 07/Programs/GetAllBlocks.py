import socket
import struct
import hashlib
import mmap
from Utils import getVarInt, setVarInt, flog
from CreateMessage import createMessage
from CreateVersionPayload import rpc_connection
from EstablishBitcoinConnection import checkMessage, \
                                parseVersionPayload, \
                                parseMsgHdr, \
                                establishConnection
from PingPong import sendPongMessage
from GetAddresses import parseAddrPayload, \
                        parseGetBlocksGetHeadersPayload, \
                        parsePingPongPayload


def getGenesisBlockHash():
    blkhash = rpc_connection.getblockhash(0)
    return blkhash

def parseSendCompactPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['announce'] = int.from_bytes(payload_m.read(1), byteorder='little')
    payload['version'] = int.from_bytes(payload_m.read(8), byteorder='little')
    return payload

def parseFeeFilterPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['feerate'] = int.from_bytes(payload_m.read(8), byteorder='little')
    return payload

mempool_l_g = []

def parseInvPayload(payload_m: mmap, payloadlen = 0):
    MSG_TX = 1
    payload = {}
    payload['count'] = getVarInt(payload_m)
    payload['inventory'] = []
    for i in range(payload['count']):
        inv = {}
        inv['type'] = int.from_bytes(payload_m.read(4), byteorder='little')
        if inv['type'] == MSG_TX:
            mempool = rpc_connection.getrawmempool(True)
            if (len(mempool_l_g) > 0):
                new_tx = set(mempool.keys()) ^ set(mempool_l_g[-1].keys())
                if len(new_tx) > 0:
                    mempool_l_g.append(mempool)
                    print('inserted mempool', file=flog)
            else:
                mempool_l_g.append(mempool)
                print('inserted mempool', file=flog)
        inv['hash'] = payload_m.read(32)[::-1].hex()
        payload['inventory'].append(inv)
    return payload

def parseBlockHeader(payload_m: mmap):
    hdr = {}
    hdr['version'] = int.from_bytes(payload_m.read(4), byteorder='little')
    hdr['prev_blockhash'] = payload_m.read(32)[::-1].hex()
    hdr['merkle_root'] = payload_m.read(32)[::-1].hex()
    hdr['timestamp'] = int.from_bytes(payload_m.read(4), byteorder='little')
    hdr['bits'] = payload_m.read(4)[::-1].hex()
    hdr['nonce'] = payload_m.read(4)[::-1].hex()
    return hdr

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

def parseHeadersPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['count'] = getVarInt(payload_m)
    payload['headers'] = []
    for i in range(payload['count']):
        hdr = {}
        start = payload_m.tell()
        h_b = hashlib.sha256(payload_m.read(80)).digest()
        hdr['blkhash'] = hashlib.sha256(h_b).digest()[::-1].hex()
        payload_m.seek(start)
        hdr['header'] = parseBlockHeader(payload_m)
        hdr['txn_count'] = getVarInt(payload_m)
        payload['headers'].append(hdr)
    return payload

def parseTxPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['version'] = int.from_bytes(payload_m.read(4), byteorder='little')
    payload['tx_in count'] = getVarInt(payload_m)
    payload['tx_in'] = []
    for i in range(payload['tx_in count']):
        txin = {}
        txin['prev_tx_hash'] = payload_m.read(32)[::-1].hex()
        txin['prev_tx_out_index'] = int.from_bytes(payload_m.read(4),
                byteorder='little')
        txin['bytes_scriptsig'] = getVarInt(payload_m)
        txin['sriptsig'] = payload_m.read(txin['bytes_scriptsig']).hex()
        txin['sequence'] = payload_m.read(4)[::-1].hex()
        payload['tx_in'].append(txin)
    payload['tx_out count'] = getVarInt(payload_m)
    payload['tx_out'] = []
    for i in range(payload['tx_out count']):
        txout = {}
        txout['satoshis'] = int.from_bytes(payload_m.read(8), byteorder='little')
        txout['bytes_scriptpubkey'] = getVarInt(payload_m)
        txout['scriptpubkey'] = payload_m.read(txout['bytes_scriptpubkey']).hex()
        payload['tx_out'].append(txout)
    payload['locktime'] = int.from_bytes(payload_m.read(4), byteorder='little')
    return payload

def parseBlockPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['version'] = int.from_bytes(payload_m.read(4), byteorder='little')
    payload['prev_blockhash'] = payload_m.read(32)[::-1].hex()
    payload['merkle_root'] = payload_m.read(32)[::-1].hex()
    payload['timestamp'] = int.from_bytes(payload_m.read(4), byteorder='little')
    payload['bits'] = payload_m.read(4)[::-1].hex()
    payload['nonce'] = payload_m.read(4)[::-1].hex()
    payload['txn_count'] = getVarInt(payload_m)
    payload['txns'] = []
    for i in range(payload['txn_count']):
        payload['txns'].append(parseTxPayload(payload_m))
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
    'feefilter': parseFeeFilterPayload,
    'inv': parseInvPayload,
#    'getdata': parseInvPayload,
#    'notfound': parseInvPayload,
#    'tx': parseTxPayload,
    'block': parseBlockPayload,
    'getblocks': parseGetBlocksGetHeadersPayload,
    'getheaders': parseGetBlocksGetHeadersPayload,
    'headers': parseHeadersPayload,
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

def createGetHeadersPayload(hdr_info_l: list, version: int):
    version_b = struct.pack('<L', version)
    blk_locator_hashes_b = b''
    count = 0
    for i in range(len(hdr_info_l) - 1, len(hdr_info_l) - 32, -1):
        if i < 1: # assuming first block is genesis
            break
        blk_locator_hashes_b += bytes.fromhex(hdr_info_l[i]['blkhash'])[::-1]
        count += 1
    blk_locator_hashes_b += bytes.fromhex(getGenesisBlockHash())[::-1]
    count += 1
    hash_count_b = setVarInt(count)
    stop_hash_b = bytes(32)
    payload = version_b \
            + hash_count_b \
            + blk_locator_hashes_b \
            + stop_hash_b
    return payload

def waitForBlock(s: socket):
    while True:
        recvmsg = recvMsg(s)
        if recvmsg['command'] == 'block':
            break
        elif recvmsg['command'] == 'ping':
            sendPongMessage(s, recvmsg)
    return recvmsg

def sendGetHeadersMessage(s: socket, hdr_info_l: list, version: int):
    sndcmd = 'getheaders'
    payload = createGetHeadersPayload(hdr_info_l, version)
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)

def waitForHeaders(s: socket):
    while True:
        recvmsg = recvMsg(s)
        if recvmsg['command'] == 'headers':
            break
        elif recvmsg['command'] == 'ping':
            sendPongMessage(s, recvmsg)
    return recvmsg

def createGetDataPayload(count: int, hash_l: list):
    MSG_BLOCK = 2
    hash_count_b = setVarInt(count)
    hashes_b = b''
    for i in range(count):
        type_b = struct.pack('<L', MSG_BLOCK)
        hashes_b += type_b + bytes.fromhex(hash_l[i]['blkhash'])[::-1]
    payload_b = hash_count_b + hashes_b
    return payload_b

def sendGetDataMessage(s: socket, count: int, hash_l: list):
    sndcmd = 'getdata'
    payload = createGetDataPayload(count, hash_l)
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)

def sendAndHandleGetHeaders(s: socket, hdr_info_l: list, version: int):
    sendGetHeadersMessage(s, hdr_info_l, version)
    recvmsg = waitForHeaders(s)
    count = recvmsg['payload']['count']
    for i in range(0, count, 16):
        lindex = i + 16 if i + 16 < count else count
        print(i, lindex)
        blk_l = recvmsg['payload']['headers'][i:lindex]
        sendGetDataMessage(s, lindex - i, blk_l)
        for j in range(i, lindex):
            waitForBlock(s)
    return recvmsg

def sendrecvHeadersData(s: socket, version: int):
    recvmsg = sendAndHandleGetHeaders(s, [], version)
    sendAndHandleGetHeaders(s, recvmsg['payload']['headers'], version)

def sendrecvHandler(s: socket, version: int):
    if establishConnection(s, version) == False:
        print('Establish connection failed', file=flog)
        return
    sendrecvHeadersData(s, version)
