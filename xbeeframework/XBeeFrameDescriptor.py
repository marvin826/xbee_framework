

class XBeeFrameDescriptor(object):
    """XBeeFrameDescriptor represents a frame described in the XBeeFramework
       frame database."""
    def __init__(self):
        super(XBeeFrameDescriptor, self).__init__()
        self._mFrameType = 0x0
        self._mDescription = "None"
        self._mXBeeDataTypes = []
        self._mLogger = None

    def __str__(self):
        tempStr = "\tXBeeFrameDescriptor\n" + \
                  "\ttype: " + str(hex(self._mFrameType)) + "\n" \
                  "\tdescription: " + self._mDescription + "\n" \
                  "\tdata types:\n"
        for dataType in self._mXBeeDataTypes:
            tempStr += str(dataType) + "\n"
        return tempStr

    def setLogger(self, logger):
        self._mLogger = logger

    def getFrameType(self):
        return self._mFrameType

    def getDescription(self):
        return self._mDescription

    def getXBeeDataTypes(self):
        return self._mXBeeDataTypes

    def read(self, json_obj):
        self._mFrameType = json_obj["type"]
        self._mDescription = json_obj["description"]

        formats = json_obj["formats"]
        for format in formats:
            if("type" in format):
                typeStr = format["type"]
                dataType = self.getDataTypeClass(typeStr)
                dataType.setLogger(self._mLogger)
                dataType.read(format)
                self._mXBeeDataTypes.append(dataType)
            else:
                if(self._mLogger is not None):
                    logMessage = "ERROR: no \"type\" specified for format\n"
                    self._mLogger.critical(logMessage)

    def getDataTypeClass(self, classname):
        # NOTE: our convention is that the module name
        # and the class name are the same
        try:
            mod = __import__(classname)
            class_ = getattr(mod, classname)
            return class_()

        except Exception, e:
            logMessage = "XBeeFrameDatabase.getReaderClass ERROR: " + \
                str(e)
            self._mLogger.critical(logMessage)
            raise e
