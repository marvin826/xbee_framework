
# frame delimiter symbol for API mode
apiFrameDelimiter = '\x7e'

# frame escape character used in API mode.
# this character indicates that the next
# character has been escaped
apiFrameEscapeIndicator = 0x7d

# escaped charater mask for API mode.
# this charater is XOR'd with a character
# that has been escaped.
apiFrameEscapeMask = 0x20

# table describing the different types of frames
# in API mode for the XBee.
apiFrameTypes = {0x00: "Invalid Frame Type",
                 0x08: "AT Command",
                 0x09: "AT Command - Queue Parameter Value",
                 0x10: "ZigBee Transmit Request",
                 0x11: "Explicit Addressing ZigBee Command Frame",
                 0x17: "Remote Command Request",
                 0x21: "Create Source Route",
                 0x88: "AT Command Response",
                 0x8a: "Modem Status",
                 0x90: "ZigBee Transmit Status",
                 0x91: "ZigBee Receive Packet(AO=0)",
                 0x92: "ZigBee IO Data Sample Rx Indicator",
                 0x94: "XBee Sensor Read Indicator(AO=0)",
                 0x95: "Node Identification Indicator(AO-0)",
                 0x97: "Remote Command Response",
                 0xa0: "Over-the-Air Firmware Update Status",
                 0xa1: "Route Record Indicator",
                 0xa3: "Many-to-One Route Request Indicator"}

# position of the frame delimiter byte in API mode
apiFrameDelimPos = 0

# position of the frame length bytes (msb,lsb) in API mode
apiFrameLenPos = [1, 2]

# position of the frame type indicator byte in API mode
apiFrameTypePos = 3
