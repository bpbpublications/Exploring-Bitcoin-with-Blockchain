import mmap
from TraverseBlockchain import getTransactionCount

if __name__ == '__main__':
    blk_h = '00e0ff376a2079af63073c47184cd091819d506f12cb6b68887c040000000000000000001036e0b1059b1ec79cb36897ccf8bc5aef4c7996897b83754ab590bb2774bc2726c0475fea0710178ffaf153fda4090100000000010100000000000000000000'
    blk_b = bytes.fromhex(blk_h)
    blk_m = mmap.mmap(-1, len(blk_b) + 1)
    blk_m.write(blk_b)
    blk_m.seek(80)
    tx_count = getTransactionCount(blk_m)
    print('Transaction Count = %d' % tx_count)
