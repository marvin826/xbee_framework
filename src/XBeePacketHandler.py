import XBeePacket as xbp
import XBeeFrameDatabase as xbfdb


class XBeePacketHandler():
    """Processes XBeePackets from an XBeeReader"""
    def __init__(self):

        directory = "j:\\Users\\Todd\\Projects\\ZigBee\\XBee Framework\data\\"
        fileName = "XBee_API_Frame_Database.db"

        self._mFrameDB = xbfdb.XBeeFrameDatabase()
        self._mFrameDB.read(directory + fileName)

    def handle(self, packet):
        tempStr = "{0:16}:\n{1:-<17}\n".format("Received packet", "")
        print tempStr, str(packet)

        descriptors = self._mFrameDB.getDescriptors()
        for desc in descriptors:
            if(desc.getFrameType() == packet.getFrameType()):
                dataTypes = desc.getXBeeDataTypes()
                for dataType in dataTypes:
                    decode = dataType.decode(packet.getProcessedBytes())
                    print decode
