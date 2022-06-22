def calculateTransactionFee(vsize: int, feerate: float):
    return feerate * vsize/1000
