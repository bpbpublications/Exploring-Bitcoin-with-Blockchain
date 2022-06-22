from GetSeedAddresses import getTestnetPeers

if __name__ == '__main__':
    peers = getTestnetPeers()
    for index in range(5):
        print(peers[index])
