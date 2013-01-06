import XBeeDataType as xbdt


class XBeeBitField(xbdt.XBeeDataType):
    """docstring for XBeeBitField"""
    def __init__(self):
        super(XBeeBitField, self).__init__()

        self._mMaskOffset = -1
        self._mMaskLength = -1
        self._mFieldType = "Unknown"
        self._mFieldOffset = -1
        self._mFieldLength = -1
        self._mSampleSize = -1
        self._mSampleOrder = "forward"
        self._mSampleNames = []

    def __str__(self):
        tempStr = super(XBeeBitField, self).__str__()
        tempStr += "\t\tmask offset : " + str(self._mMaskOffset) + "\n" + \
                   "\t\tmask length : " + str(self._mMaskLength) + "\n" + \
                   "\t\tfield type : " + self._mFieldType + "\n" + \
                   "\t\tfield offset : " + str(self._mFieldOffset) + "\n"

        if(self._mFieldType == "variable"):
            tempStr += "\t\tfield length : " + str(self._mFieldLength) +\
                       "\n"

        tempStr += "\t\tsample size : " + str(self._mSampleSize) + "\n" + \
                   "\t\tsample order : " + str(self._mSampleOrder) + "\n"
        tempStr += "\t\tsample names : [ "

        for i in range(0, len(self._mSampleNames)):
            tempStr += self._mSampleNames[i]
            if(i < len(self._mSampleNames)):
                tempStr += ", "
        tempStr += " ]\n"

        return tempStr

    def read(self, objs):
        super(XBeeBitField, self).read(objs)

        if "mask offset" in objs:
            self._mMaskOffset = objs["mask offset"]

        if "mask length" in objs:
            self._mMaskLength = objs["mask length"]

        if "field type" in objs:
            self._mFieldType = objs["field type"]

        if "field offset" in objs:
            self._mFieldOffset = objs["field offset"]

        if "field length" in objs:
            self._mFieldLength = objs["field length"]

        if "sample size" in objs:
            self._mSampleSize = objs["sample size"]

        if "sample order" in objs:
            self._mSampleOrder = objs["sample order"]

        if "sample names" in objs:
            self._mSampleNames = objs["sample names"]

        return True
