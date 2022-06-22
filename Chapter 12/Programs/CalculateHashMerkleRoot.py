import hashlib

def hashOfJoinedStr(a:str, b:str): 
    # Reverse inputs before and after hashing due to big-endian / little-endian nonsense 
    a1 = bytes.fromhex(a)[::-1] 
    b1 = bytes.fromhex(b)[::-1] 
    h = hashlib.sha256(hashlib.sha256(a1 + b1).digest()).digest() 
    return h

def buildMerkleRoot(hash_list: list): 
    if len(hash_list) < 2: 
        return hash_list[0] 
    new_hash_list = [] 
    # Process pairs. For odd length, the last is skipped 
    for i in range(0, len(hash_list) - 1, 2): 
        new_hash_list.append(hashOfJoinedStr(hash_list[i], hash_list[i + 1])[::-1].hex()) 
    # odd, hash last item twice 
    if len(hash_list) % 2 == 1: 
        new_hash_list.append(hashOfJoinedStr(hash_list[-1], hash_list[-1])[::-1].hex()) 
    return buildMerkleRoot(new_hash_list)
