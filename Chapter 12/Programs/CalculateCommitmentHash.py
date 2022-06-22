import os
import mmap
from TraverseBlockchain import getBlockIndex
from BlockFileInfoFromBlockIndex import blocks_path_g
from BitcoinHeaderFromHex import getBlockHeader
from CoinbaseTransaction import getVarInt
from SegwitCoinbaseTransaction import getCoinbaseTransactionInfo
from SegwitBlockTransaction import getTransactionInfo
from CalculateHashMerkleRoot import buildMerkleRoot, hashOfJoinedStr

def getWitnessReservedValue(cb_tx: dict): 
    return cb_tx['inputs'][0]['witnesses'][0]['witness'] 

def getRootHashes(txn_m): 
    txcount = getVarInt(txn_m) 
    wtxid_l = [] 
    txid_l = [] 
    cb_tx = getCoinbaseTransactionInfo(txn_m) 
    txid_l.append(cb_tx['txid']) 
    wtxid_l.append(bytes(32).hex()) 
    for txindex in range(txcount - 1): 
        tx = getTransactionInfo(txn_m) 
        wtxid_l.append(tx['wtxid']) 
        txid_l.append(tx['txid']) 
    witness_merkle_root_h = buildMerkleRoot(wtxid_l) 
    merkle_root_h = buildMerkleRoot(txid_l) 
    return merkle_root_h, witness_merkle_root_h, cb_tx 

def calculateCommitmentHash(blkhash_b: bytes, block_db): 
    jsonobj = getBlockIndex(blkhash_b, block_db) 
    if 'data_pos' in jsonobj: 
        txn_filepath = os.path.join(blocks_path_g, 'blk%05d.dat' % jsonobj['n_file']) 
        start = jsonobj['data_pos'] 
    elif 'undo_pos' in jsonobj: 
        txn_filepath = os.path.join(blocks_path_g, 'rev%05d.dat' % jsonobj['n_file']) 
        start = jsonobj['undo_pos'] 
    # load file to memory 
    with open(txn_filepath, 'rb') as txn_file: 
        #File is open read-only 
        with mmap.mmap(txn_file.fileno(), 0, 
                        prot = mmap.PROT_READ, 
                        flags = mmap.MAP_PRIVATE) as txn_m: 
            txn_m.seek(start) 
            blkhdr = getBlockHeader(txn_m.read(80)) 
            merkle_root_h, witness_merkle_root_h, cb_tx = getRootHashes(txn_m) 
            print('Calculated Witness Merkle Root Hash\t = %s' % witness_merkle_root_h) 
            print('Calculated Merkle Root Hash\t = %s' % merkle_root_h) 
            witness_reserved_value = getWitnessReservedValue(cb_tx) 
            print('witness_reserved_value = ', witness_reserved_value) 
            # calculate commitment hash 
            commitment_hb = hashOfJoinedStr(witness_merkle_root_h, witness_reserved_value) 
            commitment_h = commitment_hb.hex() 
            print('calculated commitment hash = ', commitment_h) 
            return commitment_h, cb_tx 

def getCommitmentHashInCbTx(cb_tx: dict): 
    for output in cb_tx['outs']: 
        if output['scriptpubkey'][:12] == '6a24aa21a9ed': 
            commitment_h = output['scriptpubkey'][12:] 
            print('Actual commitment hash = ', commitment_h) 
    return commitment_h 

def verifyCommitmentHash(cb_tx: dict, commitment_h: str): 
    if getCommitmentHashInCbTx(cb_tx) == commitment_h: 
        print('Commitment hash matches') 
    else: 
        print('Invalid commitment hash') 
