from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException 
import time
import socket
import struct 
import random 
from Utils import setVarInt

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:18332"%('test', 'test')) 

def getLastBlockHeight(): 
    height = rpc_connection.getblockcount() 
    return height 

def createUserAgent(): 
    sub_version = "/MyTestAgent:0.0.1/" 
    sub_version_b = sub_version.encode() 
    len_b = setVarInt(len(sub_version_b)) 
    return len_b + sub_version_b 

def createRecvIPAddress(ip, port): 
    service_b = struct.pack('<Q', 1) 
    ip_b = socket.inet_aton(ip) 
    ipv4_to_ipv6 = bytearray.fromhex("00000000000000000000ffff") + ip_b 
    ipv6addr_b = struct.pack('>16s', ipv4_to_ipv6) 
    port_b = struct.pack('>H', port) 
    addr_b = service_b + ipv6addr_b + port_b 
    return(addr_b) 

def createTransIPAddress(): 
    service_b = struct.pack('<Q', 1) 
    ip_b = socket.inet_aton("0.0.0.0") 
    ipv4_to_ipv6 = bytearray.fromhex("000000000000000000000000") + ip_b 
    ipv6addr_b = struct.pack('>16s', ipv4_to_ipv6) 
    port_b = struct.pack('>H', 0) 
    addr_b = service_b + ipv6addr_b + port_b 
    return(addr_b) 

def createVersionPayload(s: socket, version: int): 
    version_b = struct.pack('<L', version) 
    services_b = struct.pack('<Q', 1) 
    timestamp_b = struct.pack('<Q', int(time.time())) 
    myip, myport = s.getsockname() 
    addr_recv_b = struct.pack('<26s', createRecvIPAddress(myip, myport)) 
    addr_trans_b = struct.pack('<26s', createTransIPAddress()) 
    nonce_b = struct.pack('<Q', random.getrandbits(64)) 
    user_agent = createUserAgent() 
    user_agent_b = struct.pack('<%ds' % len(user_agent), user_agent) 
    start_height_b = struct.pack('<L', getLastBlockHeight()) 
    payload = version_b \
                + services_b \
                + timestamp_b \
                + addr_recv_b \
                + addr_trans_b \
                + nonce_b \
                + user_agent_b \
                + start_height_b 
    return payload
