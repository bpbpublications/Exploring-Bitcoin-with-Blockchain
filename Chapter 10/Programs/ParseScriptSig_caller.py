import mmap
import json
from ParseScriptSig import parseScriptSig 

if __name__ == '__main__':
    script_b = bytes.fromhex('47304402203a28d10c786907fcb71c7bf69c507d58884ea9af2e7fa3b413d4e2867eca601502205fb253d82e4daa2672842ec031584ea7a215774422aa7de3cf8928c240e2faa60121030be5aa6d5de8c6dd89d6ac4d0e2a112caf5b12801349ab30fbdf2b205f0b94b8')
    script_m = mmap.mmap(-1, len(script_b) + 1)
    script_m.write(script_b)
    script_m.seek(0)
    scriptsig = parseScriptSig(script_m)
    print(json.dumps(scriptsig, indent=4))
