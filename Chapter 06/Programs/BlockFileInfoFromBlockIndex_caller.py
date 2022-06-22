import json
from BlockFileInfoFromBlockIndex import getBlockFileIndex, block_db_g

if __name__ == '__main__':
    blk_index = getBlockFileIndex(138, block_db_g)
    print(json.dumps(blk_index, indent=4))
