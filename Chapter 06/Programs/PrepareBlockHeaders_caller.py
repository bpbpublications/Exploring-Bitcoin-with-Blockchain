from PrepareBlockHeaders import getPreviousBlockHash, calculateNextTargetThreshold, targetThreshold2bits

if __name__ == '__main__':
    block_hash_b = getPreviousBlockHash()
    print('Block Hash = %s' % block_hash_b.hex())
    tt = calculateNextTargetThreshold()
    print('Next Target Threshold = %x' % tt)
    bits = targetThreshold2bits(tt)
    print('Next bits = %s' % bits.hex())
