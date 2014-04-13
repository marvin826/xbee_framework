import json
import XBeeFrameDescriptor as xbfd


class XBeeFrameDatabase(object):

    """docstring for XBeeFrameDatabase"""
    def __init__(self):
        super(XBeeFrameDatabase, self).__init__()
        self._mDescriptors = []
        self._mLogger = None

    def __str__(self):
        tempStr = "XBeeFrameDatabase\n"
        for desc in self._mDescriptors:
            tempStr += str(desc)
        return tempStr

    def setLogger(self, logger):
        self._mLogger = logger

    def getDescriptors(self):
        return self._mDescriptors

    def read(self, filename):
        dbFile = open(filename, "r")

        objs = json.load(dbFile)

        # frame descriptions are dictionaries
        # within a simple JSON array
        for frameDesc in objs:
            fDesc = xbfd.XBeeFrameDescriptor()
            fDesc.setLogger(self._mLogger)
            fDesc.read(frameDesc)
            self._mDescriptors.append(fDesc)
