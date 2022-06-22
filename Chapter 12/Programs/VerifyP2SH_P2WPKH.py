from VerifyScript_P2SH_P2WPKH import verifyScript
from SegwitBlockTransaction import getTransactionInfo
from VerifyScript_P2PKH import bytes2Mmap

if __name__ == '__main__':
    #txid :: c137ca3dc53cd1562da3fd5ceea22c8902c3cfd28b5303ecc70675dfff71ec2d
    tx_s = '020000000001027b806bcadab5c41bd3ccab867112fa041b36e0a8aff518296713721e36aed9f10000000017160014a5736b5f1caaf929de80829ec3acc2e13187f2c5feffffff7cbecb8841826bdb493bac6706be865731e414309d3640631f3571090abfdf20000000001716001405a7ef9d2ab852d55c58e42ac2d60202b2b6c9b0feffffff0234553d00000000001976a914265d799ec0fc523faba0ec8f5ee6f0621140a78588ac9cc911000000000017a9144bc6f0e3b0b3a26135ec3e5c6f88edb80881ce2c8702473044022072ddd8d42edee4662e388b8433c15516097d3bdb8a9ccec0acc21a7f7d068132022012f0ecfeb8682236c27fb8a591512102dfd8387a99111dad25a92fe65641841b01210335c4cfa33717ecea14e644ef938c9ecbcb7bd8569e8f407a014d835a8fb94efe02483045022100c038dd6cdf67aee993416e8471664a019f1d3204602e2acf759cf3cf3852d57c022017a84cdbc515de745587d62bb2b10597800c1b20f382a5b116ea8a0424ea242d012102e5692a54cbc71cb19cbc50b886305f0df9f462eae91125b39a85804cfe7a48012b310a00'
    tx_b = bytes.fromhex(tx_s)
    tx_m = bytes2Mmap(tx_b)
    tx = getTransactionInfo(tx_m)
    verifyScript(tx, 0)