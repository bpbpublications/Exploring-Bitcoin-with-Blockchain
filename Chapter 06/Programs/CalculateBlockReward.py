def getBlockReward(block_height): 
    halving_count = block_height // 210000 
    block_reward = 50/(2**halving_count) 
    return block_reward 
