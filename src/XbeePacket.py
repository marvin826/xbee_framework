

class XbeePacket:

	def __init__(self,escaped=False):

		self.rawBytes = []
		self.processedBytes = []
		self.withEscapeChars = escaped
		self.frameDataLength = -1
		self.packetChecksum = None
		self.calculatedChecksum = None
		self.isWholePacket = False
		self.isValidPacket = True
		self.totalPacketLength = -1

	def __str__(self):
		tempStr = "raw bytes length: " + str(len(self.rawBytes)) + \
		          "\nwithEscapeChars: " + str(self.withEscapeChars) + \
		          "\nframe data lenth: " + str(self.frameDataLength) + \
		          "\npacket checksum: " + str(hex(self.packetChecksum)) + \
		          "\ncalculated checksum: " + str(hex(self.calculatedChecksum)) + \
		          "\nisWholePacket: " + str(self.isWholePacket) + \
		          "\nisValidPacket: " + str(self.isValidPacket) + \
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

	def getChecksum(self):
		return self.checksum

	def setDelimitMode(self,mode):
		self.delimitMode = mode

	def setFrameDataLength(self,length):
		self.frameDataLength = length
		self.calculatePacketLength()

	def pushRawBytes(self,raw_bytes):

		# don't take these if we're a whole
		# packet already
		if(self.isWholePacket):
			raise Exception("XbeePacket: Error: pushing raw bytes to whole packet")

		if(len(self.rawBytes) == 0):
			# make sure the first byte is '\x7e'
			if(raw_bytes[0] != '\x7e'):
				raise Exception("Bad bytes received for new packet")
		for raw_byte in raw_bytes:
			self.rawBytes.append(ord(raw_byte))
		

		# see if we have at least the packet identifier and 
		# frame packet data length bytes so far
		if(len(self.rawBytes)>=3):
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

			# grab the checksum
			self.packetChecksum = self.rawBytes[-1:][0]

			# calculate the checksum
			self.calculateChecksum()

			print self

		return self.isWholePacket

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
		if(self.calculatedChecksum!=self.packetChecksum):
			raise Exception("XbeePacket : Error: Received packet is corrupted")
		else:
			self.isValidPacket = True

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

	def isWholePacket(self):
		return self.isWholePacket