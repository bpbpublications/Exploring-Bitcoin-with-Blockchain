import mmap

flog = open('communication.log', 'wt+')

def setVarInt(n: int):
    if n < 0xfd:
        n_h = '%02x' % n
    elif n > 0xfd and n < 0xffff:
        n_h = 'fd%04x' % n
    elif n > 0xffff and n < 0xFFFFFFFF:
        n_h = 'fe%08x' % n
    else:
        n_h = 'ff%016x' % n
    return bytes.fromhex(n_h)

def getVarInt(blk_m: mmap):
    b_cnt_d = {'fd': 2, 'fe': 4, 'ff': 8}
    prefix = int.from_bytes(blk_m.read(1), byteorder='little')
    if prefix < 0xFD:
        return prefix
    else:
        b_cnt = b_cnt_d['%x' % prefix]
        size = int.from_bytes(blk_m.read(b_cnt), byteorder='little')
        return size
