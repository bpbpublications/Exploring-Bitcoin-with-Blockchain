from CalculateTransactionFees import calculateTransactionFee

if __name__ == '__main__':
    feerate = 0.00075062
    vsize = 208
    fee = calculateTransactionFee(vsize, feerate)
    print('Estimated Minimum Fee in bitcoin = ', fee)
