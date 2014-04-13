

class XBeeDataType(object):

    """docstring for XBeeDataType"""
    def __init__(self):
        self._mName = "None"
        self._mType = "Unknown"
        self._mLogger = None

    def __str__(self):
        tempStr = "\t\tname: " + self._mName + "\n" + \
                  "\t\ttype: " + self._mType + "\n"
        return tempStr

    def setLogger(self, logger):
        self._mLogger = logger

    def read(self, objs):
        if "type" in objs:
            self._mType = objs["type"]
        else:
            excStr = "XBeeDataType: ERROR: No 'type' field found during read()"
            raise Exception(excStr)

        if "name" in objs:
            self._mName = objs["name"]
        else:
            excStr = "XBeeDataType: ERROR: No 'name' field found during read()"
            raise Exception(excStr)

    def decode(self, rBytes, packet):
        return {self._mName: {"type": self._mType}}
