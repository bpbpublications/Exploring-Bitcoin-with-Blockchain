import hashlib 
blk_b = bytes.fromhex('040020200a377a6ce7bfbd5efdbe087801fbef9a8a7b6815c3eb08000000000000000000ead1c751f9b4fedd1ff1ab37f7dccec13fc4cdfd6df4406fdd72cd44655fd2fa9389286273370a1739264fbc') 
h1 = hashlib.sha256(blk_b).digest() 
h2 = hashlib.sha256(h1).digest() 
print(h2[::-1].hex())
