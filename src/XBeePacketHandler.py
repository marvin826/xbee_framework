import XBeePacket as xbp


class XBeePacketHandler():
    """Processes XBeePackets from an XBeeReader"""
    def __init__(self):
        _mDatabase = None

    def handle(self, packet):
        tempStr = "{0:16}:\n{1:-<17}\n".format("Received packet", "")
        print tempStr, str(packet)
