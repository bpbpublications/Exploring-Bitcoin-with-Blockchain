import socket
import random
from CreateVersionPayload import createVersionPayload
from GetSeedAddresses import getTestnetPeers

if __name__ == '__main__':
    peers = getTestnetPeers()
    p = random.choice(peers)
    s = None
    peerinfo = {}
    print("Trying to connect to ", p)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    err = s.connect(p)
    print('TCP Connection Established')
    payload = createVersionPayload(s, 70015)
    print('Version payload: ', payload.hex())
    s.close()
