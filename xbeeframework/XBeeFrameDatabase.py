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

    def getReaderClass(self, classname):
        # NOTE: our convention is that the module name
        # and the class name are the same
        try:
            mod = __import__(classname)
            class_ = getattr(mod, classname)
            return class_()

        except Exception, e:
            logMessage = "XBeeFrameDatabase.getReaderClass ERROR:" + \
                str(e)
            self._mLogger.critical(logMessage)
