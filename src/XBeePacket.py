import time
import xbee_constants as xbc


class XBeePacket:

    def __init__(self, escaped=False):

        self.rawBytes = []
        self.processedBytes = []
        self.withEscapeChars = escaped
        self.frameDataLength = -1
        self.packetChecksum = -1
        self.calculatedChecksum = -1
        self.isWholePacket = False
        self.isErrorFreePacket = True
        self.totalPacketLength = -1
        self.apiFrameType = 0x0
        self.timeStamp = 0.0

    def __str__(self):
        formatStr = "{0:20} : {1}\n" + \
                    "{2:20} : {3}\n" + \
                    "{4:20} : {5}\n" + \
                    "{6:20} : {7}\n" + \
                    "{8:20} : {9}\n" + \
                    "{10:20} : {11}\n" + \
                    "{12:20} : {13}\n" + \
                    "{14:20} : {15}\n" + \
                    "{16:20} : {17}\n" + \
                    "{18:20} : {19}\n"
        tempStr = \
            formatStr.format("Raw bytes length", str(len(self.rawBytes)),
                             "Frame data length", str(self.frameDataLength),
                             "Total frame length", str(self.totalPacketLength),
                             "Escaped?", str(self.withEscapeChars),
                             "Frame checksum", str(hex(self.packetChecksum)),
                             "Calculated checksum",
                             str(hex(self.calculatedChecksum)),
                             "Whole frame?", str(self.isWholePacket),
                             "Error free frame?", str(self.isErrorFreePacket),
                             "Frame type",
                             self.getFrameType(self.apiFrameType),
                             "Time received", self.getTimeStampStr())
        tempStr += "Raw Bytes:\n"
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

    def getTimeStamp(self):
        return self.timeStamp

    def getFrameType(self):
        return self.apiFrameType

    def getFrameType(self, apiFrameType):
        typeStr = "\"" + xbc.apiFrameTypes[apiFrameType] + \
                  "\" (" + str(hex(apiFrameType)) + ")"
        return typeStr

    def getTimeStampStr(self):
        localTime = time.localtime(self.timeStamp)
        return ("%4d-%02d-%02dT%02d:%02d:%02d%0+3d" %
                (localTime.tm_year,
                 localTime.tm_mon,
                 localTime.tm_mday,
                 localTime.tm_hour,
                 localTime.tm_min,
                 localTime.tm_sec,
               (time.timezone / 3600.0)))

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
            # make sure the first byte is the frame delimiter
            if(raw_bytes[0] != xbc.apiFrameDelimiter):
                raise Exception("Bad bytes received for new packet")

        # look to see if we have a partial -- meaning that
        # a new packet is starting in the middle of the raw_bytes
        # given. If so, take just the bytes up to the delimiter
        # and return the rest
        for i in range(len(raw_bytes)):
            rbyte = raw_bytes[i]
            delim_index = -1
            if(rbyte == xbc.apiFrameDelimiter and i > 0):
                delim_index = i
                my_bytes = raw_bytes[:i]
                extra_bytes = raw_bytes[i:]

        for raw_byte in my_bytes:
            self.rawBytes.append(ord(raw_byte))

        # see if we have at least the packet identifier and
        # frame packet data length bytes so far
        if(len(self.rawBytes) >= 3):
            # get the length of the frame packet data
            msb = self.rawBytes[xbc.apiFrameLenPos[0]]
            lsb = self.rawBytes[xbc.apiFrameLenPos[1]]
            self.setFrameDataLength((msb << 8) | lsb)

        # if the calculated packet length is
        # equal to the number of raw bytes we have,
        # then we have a complete packet
        if(self.totalPacketLength == len(self.rawBytes)):
            self.isWholePacket = True

            # timestamp this packet
            self.timeStamp = time.time()

            # deal with any escaped bytes
            self.processedBytes = self.processEscapedBytes(self.rawBytes)

            # grab the checksum. make sure the checksum was not
            # delimited. note: checksum is always at the end of
            # the frame
            checksum = self.rawBytes[-1:][0]
            if(self.rawBytes[-2:-1][0] == xbc.apiFrameEscapeIndicator):
                checksum = checksum ^ xbc.apiFrameEscapeMask
            self.packetChecksum = checksum

            # calculate the checksum
            self.calculateChecksum()

            # grab the frame type if we have a valid frame
            if(self.getIsValidPacket()):
                self.apiFrameType = self.rawBytes[xbc.apiFrameTypePos]

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
            if(raw_byte == xbc.apiFrameEscapeIndicator):
                delimCount += 1
        self.totalPacketLength += delimCount
        return self.totalPacketLength

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
                    "XBeePacket : Error: Received packet is corrupted\n" +
                    str(self))
            else:
                self.isErrorFreePacket = True

    def processEscapedBytes(self, raw_bytes):
        processed = []
        escaped = False
        for b in raw_bytes:
            if(b == xbc.apiFrameEscapeIndicator and self.withEscapeChars):
                escaped = True
                continue
            if(escaped):
                escaped = False
                b = b ^ xbc.apiFrameEscapeMask
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
