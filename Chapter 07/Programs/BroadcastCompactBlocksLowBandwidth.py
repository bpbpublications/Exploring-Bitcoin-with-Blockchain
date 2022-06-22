import socket
import struct
import hashlib
import mmap
import siphash
from Utils import setVarInt, flog
from CreateMessage import createMessage
from EstablishBitcoinConnection import checkMessage, \
                                parseVersionPayload, \
                                parseMsgHdr, \
                                establishConnection
from PingPong import sendPongMessage
from GetAddresses import parseAddrPayload, \
                        parsePingPongPayload, \
                        parseGetBlocksGetHeadersPayload
from GetAllBlocks import parseHeadersPayload, \
                                parseTxPayload, \
                                parseSendCompactPayload, \
                                getGenesisBlockHash, \
                                parseBlockPayload, \
                                parseInvPayload, \
                                parseFeeFilterPayload, \
                                mempool_l_g
from BroadcastBlockSendHeaders import sendSendHeadersMessage, \
                                    getBlockHashListFromCoreClient
from BroadcastCompactBlocksHighBandwidth import  createSendCompactPayload, \
                                                parseCmpctBlockPayload, \
                                                parseBlockTxnPayload

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

def createGetDataPayloadCMPCTBlock(hash_l: list): 
    MSG_CMPCT_BLOCK = 4 
    count = len(hash_l) 
    hash_count_b = setVarInt(count) 
    hashes_b = b'' 
    for i in range(count): 
        type_b = struct.pack('<L', MSG_CMPCT_BLOCK) 
        hashes_b += type_b + bytes.fromhex(hash_l[i]['blkhash'])[::-1] 
    payload_b = hash_count_b + hashes_b 
    return payload_b 

def createHeadersPayloadNoHeaders():
    cnt_b = setVarInt(0)
    headers_b = b''
    payload = cnt_b + headers_b
    return payload

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

def sendSendCompactMessage(s: socket): 
    # send sendcmpct message for Segwit 
    sndcmd = 'sendcmpct' 
    payload = createSendCompactPayload(0, 2) 
    sndmsg = createMessage(sndcmd, payload) 
    s.send(sndmsg) 
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog) 
    # send sendcmpct message for others 
    sndcmd = 'sendcmpct' 
    payload = createSendCompactPayload(0, 1) 
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

def sendGetDataMessage(s: socket, recvmsg: dict): 
    sndcmd = 'getdata' 
    blk_l = recvmsg['payload']['headers'] 
    payload = createGetDataPayloadCMPCTBlock(blk_l) 
    sndmsg = createMessage(sndcmd, payload) 
    s.send(sndmsg) 
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog) 

def waitAndHandleHeaderResponse(s: socket): 
    recvmsg = waitForHeaders(s) 
    sendGetDataMessage(s, recvmsg) 
    recvmsg = waitForCmpctBlock(s) 
    shortIDs_index_l = findMissingShortIDs(recvmsg['payload']) 
    if len(shortIDs_index_l) > 0: 
        sendGetBlockTxn(s, recvmsg, shortIDs_index_l) 
        waitForBlockTxn(s) 
#    shouldwait = (len(shortIDs_index_l) == 0)
#    print("waiting" if shouldwait == True else "done")
#    return shouldwait

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
#    shouldwait = True
#    while shouldwait == True:
#        shouldwait = \
    waitAndHandleHeaderResponse(s)

def sendrecvHandler(s: socket, version: int): 
    if establishConnection(s, version) == False: 
        print('Establish connection failed', file=flog) 
        return 
    sendrecvHeadersData(s, version) 
