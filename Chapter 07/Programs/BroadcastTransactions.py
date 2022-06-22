import socket
import struct
import mmap
from Utils import setVarInt, flog
from CreateMessage import createMessage
from EstablishBitcoinConnection import checkMessage, \
                                parseVersionPayload, \
                                parseMsgHdr, \
                                establishConnection
from PingPong import sendPongMessage
from GetAddresses import parsePingPongPayload, \
                                parseAddrPayload, \
                                parseGetBlocksGetHeadersPayload
from GetAllBlocks import parseHeadersPayload, \
                                parseTxPayload, \
                                parseBlockPayload, \
                                parseSendCompactPayload, \
                                parseFeeFilterPayload, \
                                parseInvPayload


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

def createGetDataTxPayload(payload: dict): 
    MSG_TX = 1 
    data_b = b'' 
    count = 0 
    for i in range(payload['count']): 
        # we only request data for tx 
        if payload['inventory'][i]['type'] == MSG_TX: 
            type_b = struct.pack('<L', payload['inventory'][i]['type']) 
            hash_b = bytes.fromhex(payload['inventory'][i]['hash'])[::-1] 
            data_b += type_b + hash_b 
            count += 1 
    count_b = setVarInt(count) 
    payload_b = count_b + data_b 
    return count, payload_b 

def waitForInvMessage(s: socket): 
    while True: 
        recvmsg = recvMsg(s) 
        if recvmsg['command'] == 'inv': 
            break 
        elif recvmsg['command'] == 'ping': 
            sendPongMessage(s, recvmsg) 
    print('Received INV', file=flog) 
    return recvmsg 

def waitForTxMsg(s: socket): 
    while True: 
        recvmsg = recvMsg(s) 
        if recvmsg['command'] == 'tx': 
            break 
        elif recvmsg['command'] == 'ping': 
            sendPongMessage(s, recvmsg) 

def sendGetDataMessageWithTx(s: socket, recvmsg: dict): 
    sndcmd = 'getdata' 
    count, payload = createGetDataTxPayload(recvmsg['payload']) 
    sndmsg = createMessage(sndcmd, payload) 
    s.send(sndmsg) 
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog) 
    return count 

def waitAndHandleInvTxnMessage(s: socket): 
    recvmsg = waitForInvMessage(s) 
    count = sendGetDataMessageWithTx(s, recvmsg) 
    for i in range(count): 
        waitForTxMsg(s) 

def sendrecvHeadersData(s: socket): 
    	    waitAndHandleInvTxnMessage(s) 

def sendrecvHandler(s: socket, version: int): 
    if establishConnection(s, version) == False: 
        print('Establish connection failed', file=flog) 
        return 
    sendrecvHeadersData(s) 
