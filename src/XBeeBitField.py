import XBeeDataType as xbdt


class XBeeBitField(xbdt.XBeeDataType):
    """docstring for XBeeBitField"""
    def __init__(self):
        super(XBeeBitField, self).__init__()

        self._mMaskOffset = -1
        self._mMaskLength = -1
        self._mMaskOrder = "forward"
        self._mFieldType = "Unknown"
        self._mFieldOffset = -1
        self._mFieldLength = -1
        self._mSampleSize = -1
        self._mSampleNames = []

    def __str__(self):
        tempStr = super(XBeeBitField, self).__str__()
        tempStr += "\t\tmask offset : " + str(self._mMaskOffset) + "\n" + \
                   "\t\tmask length : " + str(self._mMaskLength) + "\n" + \
                   "\t\tmask order : " + str(self._mMaskOrder) + "\n" + \
                   "\t\tfield type : " + self._mFieldType + "\n" + \
                   "\t\tfield offset : " + str(self._mFieldOffset) + "\n"

        if(self._mFieldType == "variable"):
            tempStr += "\t\tfield length : " + str(self._mFieldLength) +\
                       "\n"

        tempStr += "\t\tsample size : " + str(self._mSampleSize) + "\n" + \
                   "\t\tsample names : [ "

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

        if "mask order" in objs:
            self._mMaskOrder = objs["mask order"]

        if "field type" in objs:
            self._mFieldType = objs["field type"]

        if "field offset" in objs:
            self._mFieldOffset = objs["field offset"]

        if "field length" in objs:
            self._mFieldLength = objs["field length"]

        if "sample size" in objs:
            self._mSampleSize = objs["sample size"]

        if "sample names" in objs:
            self._mSampleNames = objs["sample names"]

        return True

    def decode(self, rbytes):
        decodedValue = super(XBeeBitField, self).decode(rbytes)

        # grab the bit mask
        bitMask = 0
        rawBytes = []
        for i in range(0, self._mMaskLength):
            rByte = rbytes[self._mMaskOffset + i]
            rawBytes.append(rByte)
            bitMask = (bitMask << 8) | rByte

        decodedValue["mask"] = bitMask
        decodedValue["raw mask"] = rawBytes

        # see if we have any samples
        if bitMask == 0:
            decodedValue["samples"] = {}
            return decodedValue

        # grab the sample data. if the field type
        # is fixed, we just use the field length
        # as the number of bytes we grab starting with
        # the offset byte. if the field is variable,
        # we have to count the bits in the mask to determine
        # how wide the field is
        fieldLength = 0
        if self._mFieldType == "fixed":
            fieldLength = self._mFieldLength
        else:
            # count how many 1 bits we have in the mask
            for i in range(0, self._mMaskLength * 8):
                if(((1 << i) & bitMask) > 0):
                    fieldLength += 1
            fieldLength = (fieldLength * self._mSampleSize) / 8

        # now grab the bytes that represent the sample data
        # we concatonate these together
        sampleData = rbytes[self._mFieldOffset:self._mFieldOffset +
                            fieldLength]
        rawSampleData = 0
        for i in range(len(sampleData)):
            rawSampleData = (rawSampleData << 8) | sampleData[i]

        # now build the mask to grab the values off
        # the mask is a field of '1' bits the width
        # of self._mSampleSize.
        sampleMask = (2 ** self._mSampleSize) - 1

        # calculate the number of samples
        numSamples = (fieldLength * 8) / self._mSampleSize

        # loop and pluck out the samples
        samples = []
        for i in range(numSamples):
            shift = i * self._mSampleSize
            currentMask = sampleMask << shift
            sample = (rawSampleData & currentMask) >> shift
            if(self._mMaskOrder == "forward"):
                samples.append(int(sample))
            else:
                samples.insert(0, int(sample))

        values = {}
        if(self._mFieldType == "fixed"):
            for i in range(len(samples)):
                if(((1 << i) & bitMask) > 0):
                    values[self._mSampleNames[i]] = samples[i]
        else:
            nextSample = 0
            for i in range(len(self._mSampleNames)):
                if(((1 << i) & bitMask) > 0):
                    values[self._mSampleNames[i]] = samples[nextSample]
                    nextSample += 1

        decodedValue["values"] = values

        decodedValue["raw samples"] = sampleData

        return decodedValue
