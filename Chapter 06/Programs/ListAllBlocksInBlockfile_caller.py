import os
from BlockFileInfoFromBlockIndex import blocks_path_g, block_db_g, getBlockFileIndex
from ListAllBlocksInBlockfile import parseSerialisedBlock

if __name__ == '__main__':
    n_file = 138
    block_filepath = os.path.join(blocks_path_g, 'blk%05d.dat' % n_file)
    block_f = open(block_filepath, 'rb')
    blk_index = getBlockFileIndex(n_file, block_db_g)
    print(blk_index)
    for i in range(blk_index['count']):
        # moves file pointer to the end of block header
        serialized_blk = parseSerialisedBlock(block_f)
        next_blk_loc = block_f.tell() - 80 + serialized_blk['blk_size']
        block_f.seek(next_blk_loc)
        print('serialized_blk = %s' % serialized_blk)
