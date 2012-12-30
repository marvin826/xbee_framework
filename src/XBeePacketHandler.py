import XBeePacket as xbp


class XBeePacketHandler():
    """Processes XBeePackets from an XBeeReader"""
    def __init__(self):
        _mDatabase = None

    def handle(self, packet):
        print "Received packet: ", str(packet)
