import random
import socket
from GetSeedAddresses import getTestnetPeers
from EstablishBitcoinConnection import establishConnection
from Utils import flog

if __name__ == '__main__':
    peers = getTestnetPeers()
    p = random.choice(peers)
    s = None
    peerinfo = {}
    print("Trying to connect to ", p, file=flog)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    err = s.connect(p)
    print('connected', file=flog)
    if establishConnection(s, 70015) == False:
        print('Establish connection failed', file=flog)
    s.close()
    flog.close()
