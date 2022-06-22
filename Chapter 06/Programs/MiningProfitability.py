import os
from TraverseBlockchain import getBlockIndex
from BlockFileInfoFromBlockIndex import block_db_g, blocks_path_g

MINER_HASH_RATE = 96 * 10**12
MINER_POWER_WATT = 2832
electricity_rates = {"rate_slabs": [{"min": 1, "max": 30, "unit_price": 4}, {"min": 31, "max": 100, "unit_price": 5.45}, {"min": 101, "max": 200, "unit_price": 7}, {"min": 201, "unit_price": 8.05}]}
CURRENT_SELL_PRICE = 3070000

def getPriceFromUnit(unit: float):
    rate_slabs = electricity_rates['rate_slabs']
    price = 0
    for slab in rate_slabs:
        if slab['min'] > unit:
                countinue
        elif ('max' in slab and slab['max']) > unit or 'max' not in slab:
                price += (unit - slab['min']) * slab['unit_price']
        else:
                price += (slab['max'] - slab['min']) * slab['unit_price']
    return price

def getTargetThreshold(bits: bytes):
    shift = bits[3]
    value = int.from_bytes(bits[0:3], byteorder='little')
    target_threshold = value * 2 ** (8 * (shift - 3))
    return target_threshold

def getNetworkHashRate(target_threshold: int):
    network_hashrate = (1<<256)/(600*target_threshold)
    return network_hashrate

def getBlockMiningRatePer10Min(hashrate: int, target_threshold: int):
    network_hashrate = getNetworkHashRate(target_threshold)
    block_mining_rate = hashrate/network_hashrate
    return block_mining_rate

def getBitcoinMiningRate(hashrate: int, bits: bytes, blk_reward: int):
    tgt_threshold = getTargetThreshold(bits)
    block_mining_rate = getBlockMiningRatePer10Min(hashrate, tgt_threshold)
    bitcoin_mining_rate = block_mining_rate * blk_reward
    return bitcoin_mining_rate

def getBitcoinMinedPerMonth(hashrate: int, bits: bytes, blk_reward: int):
    btc_mined_per_month = getBitcoinMiningRate(hashrate, bits, blk_reward) * 6 * 24 * 30
    return btc_mined_per_month

def getUnitFromPower(power: float):
    unit = power * 24 * 30 / 1000
    return unit

def getMiningPowerExpense(power: float):
    unit = getUnitFromPower(power)
    expense = getPriceFromUnit(unit)
    return expense

def miningReturn(power: float, hashrate: int, bits: bytes, blk_reward: int):
    expense = getMiningPowerExpense(power)
    btc_mined_per_month = getBitcoinMinedPerMonth(hashrate, bits, blk_reward)
    revenue = btc_mined_per_month * CURRENT_SELL_PRICE
    profit = revenue - expense
    return profit

def getBlockHeaderBytes(blk_hash: bytes): 
    jsonobj = getBlockIndex(blk_hash, block_db_g) 
    if 'data_pos' in jsonobj: 
        block_filepath = os.path.join(blocks_path_g, 'blk%05d.dat' % jsonobj['n_file']) 
        start = jsonobj['data_pos'] 
    elif 'undo_pos' in jsonobj: 
        block_filepath = os.path.join(blocks_path_g, 'rev%05d.dat' % jsonobj['n_file']) 
        start = jsonobj['undo_pos'] 
    # load file to memory 
    with open(block_filepath, 'rb') as blk_f: 
        blk_f.seek(start) 
        return blk_f.read(80) 
