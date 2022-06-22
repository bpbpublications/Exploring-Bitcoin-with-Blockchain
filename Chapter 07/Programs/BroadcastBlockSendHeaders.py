import socket
import mmap
from Utils import setVarInt, flog
from CreateMessage import createMessage
from CreateVersionPayload import getLastBlockHeight, \
                                rpc_connection
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
                                parseInvPayload, \
                                parseBlockPayload, \
                                parseFeeFilterPayload, \
                                sendGetDataMessage, \
                                sendAndHandleGetHeaders


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
    print('<== msg = %s' % msg)
    return msg

def sendSendHeadersMessage(s: socket): 
    sndcmd = 'sendheaders' 
    payload = b'' 
    sndmsg = createMessage(sndcmd, payload) 
    s.send(sndmsg) 
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog) 

def createHeadersPayloadNoHeaders(): 
    cnt_b = setVarInt(0) 
    headers_b = b'' 
    payload = cnt_b + headers_b 
    return payload 

def createHeadersPayload(hashes, stophash): 
    b_cnt_d = {'fd': 2, 'fe': 4, 'ff': 8} 
    found = False 
    for blk_hash in hashes: 
        try: 
            blk = rpc_connection.getblock(blk_hash) 
            found = True 
            break 
        except Exception as e: 
            continue 
    if found == True: 
        txcnt = 0 
        txcnt_b = setVarInt(txcnt) 
        headers_b = b'' 
        count = 0 
        while True: 
            # returns block hex 
            print('block_hash = %s' % blk_hash, file=flog) 
            blk = rpc_connection.getblock(blk_hash, False) 
            blk_b = bytes.fromhex(blk) 
            blkhdr_b = blk_b[:80] 
            headers_b += blkhdr_b + txcnt_b 
            blk = rpc_connection.getblock(blk_hash) 
            count += 1 
            if count == 2000 or 'nextblockhash' not in blk or stophash == blk_hash: 
                print(count, file=flog) 
                print(stophash, file=flog) 
                break 
            blk_hash = blk['nextblockhash'] 
        cnt_b = setVarInt(count) 
        payload = cnt_b + headers_b 
    else: 
        cnt_b = setVarInt(0) 
        headers_b = b'' 
        payload = cnt_b + headers_b 
    return payload 

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

def waitForBlock(s: socket):
    while True:
        recvmsg = recvMsg(s)
        if recvmsg['command'] == 'block':
            break
        elif recvmsg['command'] == 'ping':
            sendPongMessage(s, recvmsg)
    return recvmsg

def waitAndHandleHeaderResponse(s: socket): 
    recvmsg = waitForHeaders(s) 
    count = recvmsg['payload']['count'] 
    for i in range(0, count, 16): 
        lindex = i + 16 if i + 16 < count else count 
        blk_l = recvmsg['payload']['headers'][i:lindex] 
        sendGetDataMessage(s, lindex - i, blk_l) 
        for j in range(i, lindex): 
            waitForBlock(s) 

def getBlockHashListFromCoreClient(): 
    blkhash_l = [] 
    height = getLastBlockHeight() 
    for i in range(31, -1, -1): 
        d = {} 
        d['blkhash'] = rpc_connection.getblockhash(height - i) 
        blkhash_l.append(d) 
    return blkhash_l 

def sendrecvHeadersData(s: socket, version: int): 
    sendSendHeadersMessage(s) 
    blkhash_l = getBlockHashListFromCoreClient() 
    sendAndHandleGetHeaders(s, blkhash_l, version) 
    waitAndHandleHeaderResponse(s) 

def sendrecvHandler(s: socket, version: int): 
    if establishConnection(s, version) == False: 
        print('Establish connection failed', file=flog) 
        return 
    sendrecvHeadersData(s, version) 
