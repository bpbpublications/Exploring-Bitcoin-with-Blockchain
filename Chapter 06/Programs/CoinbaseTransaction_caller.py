import mmap
import json
from CoinbaseTransaction import getCoinbaseTransactionInfo, getVarInt

if __name__ == '__main__': 
    # trimmed block for block hash 000000000000000004ec466ce4732fe6f1ed1cddc2ed4b328fff5224276e3f6f 
    blk_b = bytes.fromhex('0400000039fa821848781f027a2e6dfabbf6bda920d9ae61b63400030000000000000000ecae536a304042e3154be0e3e9a8220e5568c3433a9ab49ac4cbb74f8df8e8b0cc2acf569fb9061806652c27fd7c0601000000010000000000000000000000000000000000000000000000000000000000000000ffffffff3f03801a060004cc2acf560433c30f37085d4a39ad543b0c000a425720537570706f727420384d200a666973686572206a696e78696e092f425720506f6f6c2fffffffff012fd8ff96000000001976a914721afdf638d570285d02d3076d8be6a03ee0794d88ac00000000') 
    blk_m = mmap.mmap(-1, len(blk_b) + 1) 
    blk_m.write(blk_b) 
    blk_m.seek(0) 
    blkhdr = blk_m.read(80) 
    blk_size = getVarInt(blk_m) 
    tx = getCoinbaseTransactionInfo(blk_m) 
    print(json.dumps(tx, indent = 4)) 
