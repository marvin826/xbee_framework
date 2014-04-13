import time
import xbee_constants as xbc


class XBeePacket:

    def __init__(self, escaped=False):

        self._mRawBytes = []
        self._mProcessedBytes = []
        self._mWithEscapeChars = escaped
        self._mFrameDataLength = -1
        self._mPacketChecksum = -1
        self._mCalculatedChecksum = -1
        self._mIsWholePacket = False
        self._mIsErrorFreePacket = True
        self._mTotalPacketLength = -1
        self._mAPIFrameType = 0x0
        self._mTimeStamp = 0.0

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
            formatStr.format("Raw bytes length", str(len(self._mRawBytes)),
                             "Frame data length", str(self._mFrameDataLength),
                             "Total frame length",
                             str(self._mTotalPacketLength),
                             "Escaped?", str(self._mWithEscapeChars),
                             "Frame checksum", str(hex(self._mPacketChecksum)),
                             "Calculated checksum",
                             str(hex(self._mCalculatedChecksum)),
                             "Whole frame?", str(self._mIsWholePacket),
                             "Error free frame?",
                             str(self._mIsErrorFreePacket),
                             "Frame type",
                             self.getFrameTypeStr(self._mAPIFrameType),
                             "Time received", self.getTimeStampStr())
        tempStr += "Raw Bytes:\n"
        tempStr += self.bytesToStr(self._mRawBytes) + "\n"
        tempStr += "Processed Bytes:\n"
        tempStr += self.bytesToStr(self._mProcessedBytes) + "\n"

        return tempStr

    def getFrameDataLenth(self):
        return self._mFrameDataLength

    def getRawBytes(self):
        return self._mRawBytes

    def getRawBytes(self, startByte, length):
        return self._mRawBytes[startByte:startByte + length]

    def getProcessedBytes(self, startByte=0, length=0):
        if(length == 0):
            return self._mProcessedBytes
        else:
            return self._mProcessedBytes[startByte:startByte + length]

    def getPacketChecksum(self):
        return self._mPacketChecksum

    def getIsWholePacket(self):
        return self._mIsWholePacket

    def getIsValidPacket(self):
        return self._mIsWholePacket and self._mIsErrorFreePacket

    def getTimeStamp(self):
        return self._mTimeStamp

    def getFrameType(self):
        return self._mAPIFrameType

    def getFrameTypeStr(self, frameType):
        typeStr = "\"" + xbc.apiFrameTypes[frameType] + \
                  "\" (" + str(hex(frameType)) + ")"
        return typeStr

    def getTimeStampStr(self):
        localTime = time.localtime(self._mTimeStamp)
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
        self._mFrameDataLength = length
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
        if(self._mIsWholePacket):
            raise Exception(
                "XBeePacket: Error: pushing raw bytes to whole packet")

        if(len(self._mRawBytes) == 0):
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
            self._mRawBytes.append(ord(raw_byte))

        # see if we have at least the packet identifier and
        # frame packet data length bytes so far
        if(len(self._mRawBytes) >= 3):
            # get the length of the frame packet data
            msb = self._mRawBytes[xbc.apiFrameLenPos[0]]
            lsb = self._mRawBytes[xbc.apiFrameLenPos[1]]
            self.setFrameDataLength((msb << 8) | lsb)

        # if the calculated packet length is
        # equal to the number of raw bytes we have,
        # then we have a complete packet
        if(self._mTotalPacketLength == len(self._mRawBytes)):
            self._mIsWholePacket = True

            # _mTimestamp this packet
            self._mTimeStamp = time.time()

            # deal with any escaped bytes
            self._mProcessedBytes = self.processEscapedBytes(self._mRawBytes)

            # grab the checksum. make sure the checksum was not
            # delimited. note: checksum is always at the end of
            # the frame
            checksum = self._mRawBytes[-1:][0]
            if(self._mRawBytes[-2:-1][0] == xbc.apiFrameEscapeIndicator):
                checksum = checksum ^ xbc.apiFrameEscapeMask
            self._mPacketChecksum = checksum

            # calculate the checksum
            self.calculateChecksum()

            # grab the frame type if we have a valid frame
            if(self.getIsValidPacket()):
                self._mAPIFrameType = self._mRawBytes[xbc.apiFrameTypePos]

        return extra_bytes

    def calculatePacketLength(self):
        # recalulate the total packet length
        #
        # length is determined by the frame packet data length,
        # plus the first 3 bytes (header, length msb, length lsb)
        # and the checksum byte on the end
        # also, if the packet is in delimited mode, we have
        # to account for delimiter bytes
        self._mTotalPacketLength = self._mFrameDataLength + 4
        delimCount = 0
        for raw_byte in self._mRawBytes:
            if(raw_byte == xbc.apiFrameEscapeIndicator):
                delimCount += 1
        self._mTotalPacketLength += delimCount
        return self._mTotalPacketLength

    def calculateChecksum(self):
        # we calculate the checksum by
        # adding the bytes after the first
        # three bytes (delimiter and length)
        # and subtracting this total from 0xFF
        if(self._mIsWholePacket):
            total = 0
            for raw_byte in self._mProcessedBytes[3:-1]:
                total += raw_byte
            self._mCalculatedChecksum = 0xff - (total & 0xff)

            # verify that this is not a corrupt packet
            if(self._mCalculatedChecksum != self._mPacketChecksum):
                raise Exception(
                    "XBeePacket : Error: Received packet is corrupted\n" +
                    str(self))
            else:
                self._mIsErrorFreePacket = True

    def processEscapedBytes(self, raw_bytes):
        processed = []
        escaped = False
        for b in raw_bytes:
            if(b == xbc.apiFrameEscapeIndicator and self._mWithEscapeChars):
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
        tempStr += "]"
        return tempStr
