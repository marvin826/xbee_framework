

class XBeePacket:

    def __init__(self, escaped=False):

        self.rawBytes = []
        self.processedBytes = []
        self.withEscapeChars = escaped
        self.frameDataLength = -1
        self.packetChecksum = None
        self.calculatedChecksum = None
        self.isWholePacket = False
        self.isErrorFreePacket = True
        self.totalPacketLength = -1

    def __str__(self):
        tempStr = "raw bytes length: " + str(len(self.rawBytes)) + \
                  "\nwithEscapeChars: " + str(self.withEscapeChars) + \
                  "\nframe data lenth: " + str(self.frameDataLength) + \
                  "\npacket checksum: " + str(hex(self.packetChecksum)) + \
                  "\ncalculated checksum: " + \
                  str(hex(self.calculatedChecksum)) + \
                  "\nisWholePacket: " + str(self.isWholePacket) + \
                  "\nisErrorFreePacket: " + str(self.isErrorFreePacket) + \
                  "\ntotalPacketLength: " + str(self.totalPacketLength)
        tempStr += "\nRaw Bytes:\n"
        tempStr += self.bytesToStr(self.rawBytes)
        tempStr += "Processed Bytes:\n"
        tempStr += self.bytesToStr(self.processedBytes)

        return tempStr

    def getFrameDataLenth(self):
        return self.frameDataLength

    def getRawBytes(self):
        return self.getRawBytes

    def getProcessedBytes(self):
        return self.getProcessedBytes

    def getPacketChecksum(self):
        return self.packetChecksum

    def getIsWholePacket(self):
        return self.isWholePacket

    def getIsValidPacket(self):
        return self.isWholePacket and self.isErrorFreePacket

    def setDelimitMode(self, mode):
        self.delimitMode = mode

    def setFrameDataLength(self, length):
        self.frameDataLength = length
        self.calculatePacketLength()

    def pushRawBytes(self, raw_bytes):

        # buffer for bytes that are not mine. I may
        # receive a buffer that has my bytes and bytes
        # of the next packet in it. we take our bytes
        # and return the rest to the caller
        extra_bytes = []
        my_bytes = raw_bytes

        # don't take these if we're a whole
        # packet already
        if(self.isWholePacket):
            raise Exception(
                "XBeePacket: Error: pushing raw bytes to whole packet")

        if(len(self.rawBytes) == 0):
            # make sure the first byte is '\x7e'
            if(raw_bytes[0] != '\x7e'):
                raise Exception("Bad bytes received for new packet")

        # look to see if we have a partial -- meaning that
        # a new packet is starting in the middle of the raw_bytes
        # given. If so, take just the bytes up to the delimiter
        # and return the rest
        for i in range(len(raw_bytes)):
            rbyte = raw_bytes[i]
            delim_index = -1
            if(rbyte == '\x7e' and i > 0):
                delim_index = i
                my_bytes = raw_bytes[:i]
                extra_bytes = raw_bytes[i:]

        for raw_byte in my_bytes:
            self.rawBytes.append(ord(raw_byte))

        # see if we have at least the packet identifier and
        # frame packet data length bytes so far
        if(len(self.rawBytes) >= 3):
            # get the length of the frame packet data
            msb = self.rawBytes[1]
            lsb = self.rawBytes[2]
            self.setFrameDataLength((msb << 8) | lsb)

        # if the calculated packet length is
        # equal to the number of raw bytes we have,
        # then we have a complete packet
        if(self.totalPacketLength == len(self.rawBytes)):
            self.isWholePacket = True

            # deal with any escaped bytes
            self.processedBytes = self.processEscapedBytes(self.rawBytes)

            # grab the checksum. make sure the checksum was not
            # delimted
            checksum = self.rawBytes[-1:][0]
            if(self.rawBytes[-2:-1][0] == 0x7d):
                checksum = checksum ^ 0x20
            self.packetChecksum = checksum

            # calculate the checksum
            self.calculateChecksum()

        return extra_bytes

    def calculatePacketLength(self):
        # recalulate the total packet length
        #
        # length is determined by the frame packet data length,
        # plus the first 3 bytes (header, length msb, length lsb)
        # and the checksum byte on the end
        # also, if the packet is in delimited mode, we have
        # to account for delimiter bytes
        self.totalPacketLength = self.frameDataLength + 4
        delimCount = 0
        for raw_byte in self.rawBytes:
            if(raw_byte == 0x7d):
                delimCount += 1
        self.totalPacketLength += delimCount

    def calculateChecksum(self):
        # we calculate the checksum by
        # adding the bytes after the first
        # three bytes (delimiter and length)
        # and subtracting this total from 0xFF
        if(self.isWholePacket):
            total = 0
            for raw_byte in self.processedBytes[3:-1]:
                total += raw_byte
            self.calculatedChecksum = 0xff - (total & 0xff)

            # verify that this is not a corrupt packet
            if(self.calculatedChecksum != self.packetChecksum):
                raise Exception(
                    "XBeePacket : Error: Received packet is corrupted" +
                    str(self))
            else:
                self.isErrorFreePacket = True

    def processEscapedBytes(self, raw_bytes):
        processed = []
        escaped = False
        for b in raw_bytes:
            if(b == 0x7d and self.withEscapeChars):
                escaped = True
                continue
            if(escaped):
                escaped = False
                b = b ^ 0x20
            processed.append(b)
        return processed

    def bytesToStr(self, rawBytes):
        length = len(rawBytes)
        tempStr = str(length) + " ["
        for i in range(length):
            tempStr += "\'" + hex(rawBytes[i]) + "\'"
            if(i < (length - 1)):
                tempStr += ', '
        tempStr += "]\n"
        return tempStr
