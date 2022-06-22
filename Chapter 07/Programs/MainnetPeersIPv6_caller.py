from MainnetPeersIPv6 import getMainnetPeers

if __name__ == '__main__':
    peers = getMainnetPeers()
    for peer in peers:
        print('%s\t\t\t%d' % (peer['ipaddr'], peer['port']))
