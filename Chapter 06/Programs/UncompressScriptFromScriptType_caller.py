from UncompressScriptFromScriptType import uncompressScriptType0

if __name__ == '__main__': 
    script_data = bytes.fromhex('3eba92179cd0b4caff74e3e81a14399e3c1b7ca3') 
    script = uncompressScriptType0(script_data) 
    print('script = %s' % script.hex()) 
