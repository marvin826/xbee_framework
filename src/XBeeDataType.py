

class XBeeDataType(object):
    """docstring for XBeeDataType"""
    def __init__(self):
        self._mName = "None"
        self._mType = "Unknown"

    def __str__(self):
        tempStr = "\t\tname: " + self._mName + "\n" + \
                  "\t\ttype: " + self._mType + "\n"
        return tempStr

    def read(self, objs):
        if "type" in objs:
            self.mType = objs["type"]
        else:
            return False

        if "name" in objs:
            self._mName = objs["name"]
        else:
            return False

        return True

    def decode(self, rBytes):
        return {"name": self._mName}
