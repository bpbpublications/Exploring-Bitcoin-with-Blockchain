import random
import socket
from GetSeedAddresses import getTestnetPeers
from BroadcastBlockSendHeaders import sendrecvHandler
from Utils import flog

if __name__ == '__main__':
    peers = getTestnetPeers()
    print(peers)
    p = random.choice(peers)
    s = None
    peerinfo = {}
    print("Trying to connect to ", p, file=flog)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    err = s.connect(p)
    print('connected', file=flog)
    sendrecvHandler(s, 70013)
    s.close()
    flog.close()
