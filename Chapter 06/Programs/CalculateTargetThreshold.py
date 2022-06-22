def getTargetThreshold(bits: bytes): 
    shift = bits[3] 
    value = int.from_bytes(bits[0:3], byteorder='little') 
    target_threshold = value * 2 ** (8 * (shift - 3)) 
    return target_threshold 
