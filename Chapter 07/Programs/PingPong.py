import socket
import struct
import mmap
from Utils  import flog
from CreateMessage import createMessage

def createPongPayload(nonce: int): 
    nonce_b = struct.pack('<Q', nonce) 
    return nonce_b 

def sendPongMessage(s: socket, recvmsg: dict): 
    # send pong message 
    sndcmd = 'pong' 
    nonce = recvmsg['payload']['nonce'] 
    payload = createPongPayload(nonce) 
    sndmsg = createMessage(sndcmd, payload) 
    s.send(sndmsg) 
    print('==> cmd = %s, msg = %s' % (sndcmd, sndmsg.hex()), file=flog) 
