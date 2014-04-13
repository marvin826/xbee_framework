import XBeeDataType as xbdt


class XBeeAddress(xbdt.XBeeDataType):
    """docstring for XBeeAddress"""
    def __init__(self):
        super(XBeeAddress, self).__init__()
        self._mOffset = -1
        self._mLength = 0
        self._mEnumeration = {}

    def __str__(self):
        tempStr = super(XBeeAddress, self).__str__()
        tempStr += "\t\toffset : " + str(self._mOffset) + "\n" + \
                   "\t\tlength : " + str(self._mLength) + "\n"

        return tempStr

    def read(self, objs):
        super(XBeeAddress, self).read(objs)

        if "offset" in objs:
            self._mOffset = objs["offset"]
        else:
            logStr = "ERROR: XBeeAddress requires an \"offset\" field"
            self._mLogger.critical(logStr)
            raise Exception(logStr)

        if "length" in objs:
            self._mLength = objs["length"]
        else:
            logStr = "ERROR: XBeeAddress (" + name + \
                ") requires an \"length\" field"
            self._mLogger.critical(logStr)
            raise Exception(logStr)

    def decode(self, rBytes, packet):
        parentDecode = super(XBeeAddress, self).decode(rBytes, packet)
        decodedValue = parentDecode[self._mName]

        value = 0
        rawBytes = []
        octets = []
        outRawBytes = []

        # addresses are in 2 byte octets, so the length
        # needs to be even
        if(self._mLength % 2 != 0):
            logStr = "ERROR: Length of address is not even for " +\
                self._mName
            self._mLogger.critical(logStr)
            raise Exception(logStr)

        for i in range(0, self._mLength):
            rByte = rBytes[self._mOffset + i]
            rawBytes.append(rByte)
            outRawBytes.append(hex(rByte))
            if(i > 0 and ((i + 1) % 2 == 0)):
                value = (rawBytes[i - 1] << 8) | rawBytes[i]
                octets.append(value)

        decodedValue["address"] = self.formatAddress(octets)
        decodedValue["raw"] = outRawBytes

        return parentDecode

    def formatAddress(self, octets):
        tempStr = ""
        for i in range(0, len(octets)):
            octet = octets[i]
            tempStr += "{0:04x}".format(octet)
            if(i < len(octets) - 1):
                tempStr += " "
        return tempStr
