import XBeeDataType as xbdt


class XBeeInt(xbdt.XBeeDataType):
    """docstring for XBeeInt"""
    def __init__(self):
        super(XBeeInt, self).__init__()
        self._mOffset = -1
        self._mLength = 0
        self._mEnumeration = {}

    def __str__(self):
        tempStr = super(XBeeInt, self).__str__()
        tempStr += "\t\toffset : " + str(self._mOffset) + "\n" + \
                   "\t\tlength : " + str(self._mLength) + "\n"
        enumLen = len(self._mEnumeration.keys())
        if(enumLen > 0):
            tempStr += "\t\tenums : {\n"
            count = 0
            for enum in self._mEnumeration.keys():
                tempStr += "\t\t\t" + enum + ": " + self._mEnumeration[enum]
                if(count < enumLen - 1):
                    tempStr += ",\n"
                else:
                    tempStr += " }\n"
                count += 1

        return tempStr

    def read(self, objs):
        super(XBeeInt, self).read(objs)

        if "offset" in objs:
            self._mOffset = objs["offset"]
        else:
            logStr = "ERROR: XBeeInt requires an \"offset\" field"
            self._mLogger.critical(logStr)
            raise Exception(logStr)

        if "length" in objs:
            self._mLength = objs["length"]
        else:
            logStr = "ERROR: XBeeInt (" + name \
                + ") requires an \"length\" field"
            self._mLogger.critical(logStr)
            raise Exception(logStr)

        if "enumeration" in objs:
            self._mEnumeration = objs["enumeration"]

    def decode(self, rBytes):
        decodedValue = super(XBeeInt, self).decode(rBytes)

        value = 0
        rawBytes = []
        for i in range(0, self._mLength):
            rByte = rBytes[self._mOffset + i]
            rawBytes.append(rByte)
            value = (value << 8) | rByte

        decodedValue["int"] = value
        decodedValue["raw"] = rawBytes

        enumLength = len(self._mEnumeration)
        if(enumLength > 0):
            if(value >= 0 and value < enumLength):
                decodedValue["enumeration"] = self._mEnumeration[value]
            else:
                logStr = "ERROR: Decoded value (" + str(value) + \
                         ") not in enumeration for " + \
                         self._mName
                self._mLogger.critical(logStr)
                raise Exception(logStr)

        return decodedValue
