from CalculateHashMerkleRoot import buildMerkleRoot
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%("test", "test"))

if __name__ == '__main__':
    block_hash = rpc_connection.getblockhash(715735)
    block = rpc_connection.getblock(block_hash)
    print('Merkle Root from RPC call\t = %s' % block['merkleroot'])
    hash_merkle_root = buildMerkleRoot(block['tx'])
    print('Calculated Merkle Root\t\t = %s' % hash_merkle_root)
