import requests 
import socket 
from urllib.parse import urlparse 

def isValidIPv6Addr(addr: str): 
    try: 
        socket.inet_pton(socket.AF_INET6, addr) 
    except socket.error: 
            return False 
    return True 

def parseNodeInfo(ip_port: str, nodeinfo: dict): 
    node = {} 
    node['selected'] = False 
    node['port'] = int(ip_port.split(':')[-1]) 
    val = ip_port.rsplit(':', 1)[0] 
    parsed = urlparse('//{}'.format(val)) 
    addr = parsed.hostname 
    if isValidIPv6Addr(addr) == False: 
        return node 
    node['selected'] = True 
    node['ipaddr'] = addr 
    node['type'] = nodeinfo[11] 
    node['time'] = nodeinfo[2] 
    return node 

def getMainnetPeers(): 
    url = 'https://bitnodes.io/api/v1/snapshots/latest/' 
    headers = {'Accept': 'application/json'} 
    r = requests.get(url=url, headers=headers) 
    jsonobj = r.json() 
    peers = [] 
    for k, v in jsonobj['nodes'].items(): 
        node = parseNodeInfo(k, v) 
        if node['selected'] == True: 
            peers.append(node) 
    return peers 
