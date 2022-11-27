def getBasicDISCOVER(XID, CHADDR):
    bxid = bytes.fromhex(hex(XID)[2:].zfill(8))
    #
    bchaddr = bytes.fromhex(hex(CHADDR)[2:].zfill(12))
    return b'\x01\x01\x06\x00' + \
           bxid + \
           b'\x00\x00\x00\x00' + \
           b'\x00\x00\x00\x00' + \
           b'\x00\x00\x00\x00' + \
           b'\x00\x00\x00\x00' + \
           b'\x00\x00\x00\x00' + \
           bchaddr + b'\x00\x00' + \
           b'\x00\x00\x00\x00' + \
           b'\x00\x00\x00\x00' + \
           b'\x00' * 192
