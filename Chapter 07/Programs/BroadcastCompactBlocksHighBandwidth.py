import socket
import struct
import hashlib
import mmap
import siphash
from Utils import getVarInt, setVarInt, flog
from CreateMessage import createMessage
from EstablishBitcoinConnection import checkMessage, \
                                parseVersionPayload, \
                                parseMsgHdr, \
                                establishConnection
from PingPong import sendPongMessage
from GetAddresses import parseAddrPayload, \
                        parsePingPongPayload, \
                        parseGetBlocksGetHeadersPayload
from GetAllBlocks import parseSendCompactPayload, parseBlockHeader, \
                                parseHeadersPayload, \
                                parseTxPayload, \
                                parseBlockPayload, \
                                getGenesisBlockHash, \
                                parseInvPayload, \
                                parseFeeFilterPayload, \
                                mempool_l_g
from BroadcastBlockSendHeaders import getBlockHashListFromCoreClient

def parseShortIds(payload_m: mmap, shortids_len: int):
    shortids = []
    for i in range(shortids_len):
        shortids.append(payload_m.read(6).hex())
    return shortids

def parsePrefilledTxn(payload_m: mmap, prefilledtxn_len: int):
    prefilledtxn_l = []
    for i in range(prefilledtxn_len):
        prefilledtxn = {}
        prefilledtxn['index'] = getVarInt(payload_m)
        prefilledtxn['tx'] = parseTxPayload(payload_m)
        prefilledtxn_l.append(prefilledtxn)
    return prefilledtxn_l

def parseCmpctBlockPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    pos = payload_m.tell()
    payload['hdr_nonce'] = payload_m.read(88).hex()
    payload_m.seek(pos)
    payload['header'] = parseBlockHeader(payload_m)
    payload['nonce'] = payload_m.read(8)[::-1].hex()
    payload['shortids_length'] = getVarInt(payload_m)
    payload['shortids'] = parseShortIds(payload_m, payload['shortids_length'])
    payload['prefilledtxn_length'] = getVarInt(payload_m)
    payload['prefilledtxn'] = parsePrefilledTxn(payload_m, payload['prefilledtxn_length'])
    return payload

def parseBlockTxnPayload(payload_m: mmap, payloadlen = 0):
    payload = {}
    payload['blkhash'] = payload_m.read(32)[::-1].hex()
    payload['txn_len'] = getVarInt(payload_m)
    payload['txn'] = []
    for i in range(payload['txn_len']):
        txn = parseTxPayload(payload_m)
        payload['txn'].append(txn)
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
    'tx': parseTxPayload,
    'block': parseBlockPayload,
    'getblocks': parseGetBlocksGetHeadersPayload,
    'getheaders': parseGetBlocksGetHeadersPayload,
    'headers': parseHeadersPayload,
#    'reject': parseRejectPayload,
    'sendcmpct': parseSendCompactPayload,
    'cmpctblock': parseCmpctBlockPayload,
#    'getblocktxn': parseGetBlockTxnPayload,
    'blocktxn': parseBlockTxnPayload
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
    print('<== msg = %s' % msg)
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

def createSendCompactPayload(announce: int, version: int):
    announce_b = struct.pack('<B', announce)
    version_b = struct.pack('<Q', version)
    payload = announce_b + version_b
    return payload

def createHeadersPayloadNoHeaders():
    cnt_b = setVarInt(0)
    headers_b = b''
    payload = cnt_b + headers_b
    return payload

def createGetBlockTxnPayload(payload: dict, shortIDs_index_l: list):
    hdr_b = bytes.fromhex(payload['hdr_nonce'])[0:80] #header
    blkhash_b = hashlib.sha256(hashlib.sha256(hdr_b).digest()).digest()
    print('blkhash = %s' % blkhash_b[::-1].hex())
    indexes_len_b = setVarInt(len(shortIDs_index_l))
    indexes_b = b''
    for shortIDs_index in shortIDs_index_l:
        indexes_b += setVarInt(shortIDs_index)
    payload = blkhash_b + indexes_len_b + indexes_b
    return payload

def sendSendHeadersMessage(s: socket):
    sndcmd = 'sendheaders'
    payload = b''
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)

def sendSendCompactMessage(s: socket):
    # send sendcmpct message for Segwit
    sndcmd = 'sendcmpct'
    payload = createSendCompactPayload(1, 2)
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)
    # send sendcmpct message for others
    sndcmd = 'sendcmpct'
    payload = createSendCompactPayload(1, 1)
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)

def sendHeadersMessage(s: socket):
    # send header message
    sndcmd = 'headers'
    payload = createHeadersPayloadNoHeaders()
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)

def convertTxIDs2ShortIDs(payload: dict, txid_l: list):
    hdr_nonce_b = bytes.fromhex(payload['hdr_nonce'])
    shortids_l = []
    for txid in txid_l:
        txid_b = bytes.fromhex(txid)[::-1]
        h_b = hashlib.sha256(hdr_nonce_b).digest()[0:16]
        sip = siphash.SipHash_2_4(h_b, txid_b)
        siphash_b = sip.digest()
        shortid = siphash_b[:-2].hex()
        shortid_l = siphash_b[2:].hex()
        shortids_l.append(shortid)
    return shortids_l

def findMissingShortIDs(payload: dict):
    for i in range(len(mempool_l_g)):
        stored_mempool = mempool_l_g[-1-i]
        txid_l = []
        for k, v in stored_mempool.items():
            if 'wtxid' in v:
                txid_l.append(v['wtxid'])
            else:
                txid_l.append(k)
        shortIDs = convertTxIDs2ShortIDs(payload, txid_l)
        shortIDs_index_l = []
        for recvd_shortID in payload['shortids']:
            if recvd_shortID not in shortIDs:
                shortIDs_index_l.append(payload['shortids'].index(recvd_shortID) + 1)
        if len(shortIDs_index_l) > 0:
            break
    return shortIDs_index_l

def waitForCmpctBlock(s: socket):
    while True:
        recvmsg = recvMsg(s)
        if recvmsg['command'] == 'cmpctblock':
            return recvmsg
        elif recvmsg['command'] == 'ping':
            sendPongMessage(s, recvmsg)
    return recvmsg

def sendGetBlockTxn(s: socket, recvmsg: dict, shortIDs_index_l):
    sndcmd = 'getblocktxn'
    payload = createGetBlockTxnPayload(recvmsg['payload'], shortIDs_index_l)
    sndmsg = createMessage(sndcmd, payload)
    s.send(sndmsg)
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog)

def waitForBlockTxn(s: socket):
    while True:
        recvmsg = recvMsg(s)
        if recvmsg['command'] == 'blocktxn':
            return recvmsg
        elif recvmsg['command'] == 'ping':
            sendPongMessage(s, recvmsg)

def waitAndHandleHeaderResponse(s: socket):
    recvmsg = waitForCmpctBlock(s)
    shortIDs_index_l = findMissingShortIDs(recvmsg['payload'])
    if len(shortIDs_index_l) > 0:
        sendGetBlockTxn(s, recvmsg, shortIDs_index_l)
        waitForBlockTxn(s)

def waitForHeaders(s: socket):
    while True:
        recvmsg = recvMsg(s)
        if recvmsg['command'] == 'headers':
            break
        elif recvmsg['command'] == 'ping':
            sendPongMessage(s, recvmsg)
        elif recvmsg['command'] == 'getheaders':
            sendHeadersMessage(s)
    return recvmsg

def sendGetHeadersMessage(s: socket, hdr_info_l: list, version: int):
    sndcmd = 'getheaders'
    payload = createGetHeadersPayload(hdr_info_l, version)
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
    sendSendHeadersMessage(s)
    sendSendCompactMessage(s)
    blkhash_l = getBlockHashListFromCoreClient()
    sendAndHandleGetHeaders(s, blkhash_l, version)
    waitAndHandleHeaderResponse(s)

def sendrecvHandler(s: socket, version: int):
    if establishConnection(s, version) == False:
        print('Establish connection failed', file=flog)
        return
    sendrecvHeadersData(s, version)
