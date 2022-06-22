from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException 
import json 
import pandas as pd 
from pandas import DataFrame 
import numpy as np 
import copy 
import hashlib 
from CalculateHashMerkleRoot import buildMerkleRoot

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%("test", "test"))

def findAllDependentTx(mempool: dict, k: str):
    tx_l = [k]
    vsize = mempool[k]['vsize']
    fee = mempool[k]['fees']['base']
    if len(mempool[k]['depends']) == 0:
        return tx_l, vsize, fee
    for dependent in mempool[k]['depends']:
        dep_tx_l, dep_vsize, dep_fee = findAllDependentTx(mempool, dependent)
        tx_l.extend(dep_tx_l)
        vsize += dep_vsize
        fee += dep_fee
    return tx_l, vsize, fee

def getMempoolTxList():
    mempool = rpc_connection.getrawmempool(True)
    tx_l = []
    for k, v in mempool.items():
        dep_l, vsize, fee = findAllDependentTx(mempool, k)
        dep_l.remove(k) # remove itself from list of dependents
        sats_per_byte = fee*10**8/vsize
        tx_l.append({'txid': k, 'sats_per_byte': sats_per_byte, 'vsize': vsize, 'depends': dep_l})
    return tx_l, mempool

def getSortedDF(tx_l: list):
    df = pd.DataFrame(tx_l)
    df = df.sort_values(by=['sats_per_byte'], ascending = False)
    df = df.reset_index(drop=True)
    return df

def pruneDF(df):
    vsize = 0
    mb = 1 << 20
    inc_l = []
    for index, row in df.iterrows():
        if row['vsize'] + vsize > mb:
            df.drop(index, inplace=True)
        else:
            if row['txid'] in inc_l:
                df.drop(index, inplace=True)
                continue
            inc_l.extend(row['depends'])
            vsize += row['vsize']
    return df, inc_l

def updateWithDepends(df, depend_l: list, mempool):
    tx_l = []
    for dep in depend_l:
        vsize = mempool[dep]['vsize']
        fee = mempool[dep]['fees']['base']
        sats_per_byte = fee*10**8/vsize
        tx_l.append({'txid': dep,
                    'sats_per_byte': sats_per_byte,
                    'vsize': vsize,
                    'depends': []}) # ignore dependents
    df2 = pd.DataFrame(tx_l)
    df.append(df2, ignore_index = True)
    return df

def getMempoolTx():
    tx_l, mempool = getMempoolTxList()
    df = getSortedDF(tx_l)
    df, depend_l = pruneDF(df)
    df = updateWithDepends(df, depend_l, mempool)
    final_tx_l = df['txid'].tolist()
    sum_vsize = 0
    for tx in final_tx_l:
        sum_vsize += mempool[tx]['vsize']
    print('sum_vsize = ', sum_vsize)
    print('tx count = ', len(final_tx_l))
    return(final_tx_l)

#def getRawTransaction(txid: str):
#    rawtx = rpc_connection.getrawtransaction(txid)
#    return rawtx
#
#def hashOfJoinedStr(a:str, b:str):
#     # Reverse inputs before and after hashing due to big-endian / little-endian nonsense
#     a1 = bytes.fromhex(a)[::-1]
#     b1 = bytes.fromhex(b)[::-1]
#     h = hashlib.sha256(hashlib.sha256(a1 + b1).digest()).digest()
#     return h[::-1].hex()

if __name__ == '__main__':
    txl = getMempoolTx()
    mrh = buildMerkleRoot(txl)
    print(mrh)

