from CalculateTargetThreshold import getTargetThreshold

if __name__ == '__main__':
    bits = bytes.fromhex("170b98ab")[::-1] 
    target_threshold = getTargetThreshold(bits) 
    print('Target Threshold = %x' % target_threshold) 
    block_hash = 0x00000000000000000004db407202aff54e9ace0efb72588bb73a2beebb248c28 
    print('Block Hash = %x' % block_hash) 
    print('Valid' if target_threshold > block_hash else 'Invalid') 
