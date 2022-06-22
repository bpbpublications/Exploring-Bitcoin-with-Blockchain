import bech32 

witprog = bytes.fromhex('122bf8b77dceee01c0fa1f2b36d155fea2a5b016') 
witver = 0x00 
hrp = 'bc' 
address = bech32.encode(hrp, witver, witprog) 
print(address) 
