import XBeePacket as xbp


class XBeeReader():
    """Reads from an XBee radio through the computer's \
       serial connection."""
    def __init__(self):
        self._mXBeeConnection = None
        self._mPacketHandler = None

    def setHandler(self, handler):
        self._mPacketHandler = handler

    def setConnection(self, connection):
        self._mXBeeConnection = connection

    def read(self, escaped=False):
        # clean out the buffer so
        # we don't get any junk
        self._mXBeeConnection.flushInputBuffer()

        # initialize our buffers for reading
        currentPacket = xbp.XBeePacket(escaped)
        byte_buffer = []
        extra_bytes = []

        # now read the connection. we read the serial
        # connection one byte at a time. the connection's
        # "read" method blocks until a byte is ready to
        # be read in. we keep reading until the connection
        # has no more bytes to be read. when this happens,
        # we push the read bytes to an XBeePacket object,
        # which then constructs the packet. when a valid
        # packet is ready, we hand the packet to a handler,
        # create a new packet instance, and wait to read
        # bytes again
        while(True):

            raw_byte = self._mXBeeConnection.getNextByte()
            byte_buffer.append(raw_byte)
            if(self._mXBeeConnection.moreBytesAvailable() is False):

                extra_bytes = currentPacket.pushRawBytes(byte_buffer)
                if(currentPacket.getIsValidPacket() is True):
                    if(self._mPacketHandler):
                        self._mPacketHandler.handle(currentPacket)

                    currentPacket = xbp.XBeePacket(escaped)

                byte_buffer = extra_bytes
