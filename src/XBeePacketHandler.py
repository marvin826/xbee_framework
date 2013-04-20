import XBeePacket as xbp
import XBeeFrameDatabase as xbfdb
import json


class XBeePacketHandler():
    """Processes XBeePackets from an XBeeReader"""
    def __init__(self):

        self._mFrameDB = False
        self._mLogger = None

    def setDatabase(self, frameDatabase):
        self._mFrameDB = frameDatabase
        if(self._mLogger is not None):
            self._mFrameDB.setLogger(self._mLogger)

    def setLogger(self, logger):
        self._mLogger = logger

    def handle(self, packet):
        if(self._mFrameDB is True):
            return

        self.logMessage("Received packet", "debug")
        self.logMessage(str(packet), "debug")

        descriptors = self._mFrameDB.getDescriptors()
        for desc in descriptors:
            if(desc.getFrameType() == packet.getFrameType()):
                dataTypes = desc.getXBeeDataTypes()
                decodedPacket = []
                for dataType in dataTypes:
                    try:
                        decode = dataType.decode(packet.getProcessedBytes())
                        decodedPacket.append(decode)
                    except Exception, e:
                        logStr = "XBeePacketHandler: " \
                            + "ERROR: Error decoding packet"
                        self.logMessage(logStr, "critical")
                        raise Exception(logStr)
                jsonStr = json.dumps(decodedPacket)
                self.logMessage(jsonStr, "debug")
                return jsonStr

    def logMessage(self, message, level="info"):
        if(self._mLogger is not None):
            if(level is "info"):
                self._mLogger.info(message)
            elif(level is "debug"):
                self._mLogger.debug(message)
            elif(level is "critical"):
                self._mLogger.critical(message)
