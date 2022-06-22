from BlockFileInfoFromBlockIndex import block_db_g
from CalculateCommitmentHash import calculateCommitmentHash, verifyCommitmentHash

if __name__ == '__main__':
    blk_hb = bytes.fromhex('00000000000000000000f608724d1e152a875384e5ed06ae4a889c5a6c19c2f1')[::-1]
    commitment_h, cb_tx = calculateCommitmentHash(blk_hb, block_db_g)
    verifyCommitmentHash(cb_tx, commitment_h)
