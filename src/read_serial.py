import serial
import serial.tools.list_ports
import logging
import XbeePacket as xbp

currentPacket = xbp.XbeePacket(True)
packets = []

# initialize the serial port for communications.
# If successful, this returns a Serial object.
# If not successful, this throws a SerialException
def init_comm(port="COM4"):
	# open the serial port to read
    # information
    ser = serial.Serial(port,9600,timeout=None)
    return ser

def test_positive_init_comm():

	try:
		ser = init_comm("COM6")
		print "Successfully opened serial port: " + ser.portstr
		ser.close()
	except serial.SerialException as se:
		print se
		ports = serial.tools.list_ports.comports()
		print "Available ports:"
		print ""
		print "%4s\t%-40.40s\t%-40.40s" % ('Name','Description','Port Type')
		print "%4s\t%-40.40s\t%-40.40s" % ('-'*4,'-'*40,'-'*40)
		for port in ports:
			name,desc,port_type = port
			print "%4s\t%-40.40s\t%-40.40s" % (name,desc,port_type)

test_positive_init_comm()

ser = init_comm("COM6")

byte_buffer = []

ser.flushInput()

while(True):
	raw_byte = ser.read(1)
	byte_buffer.append(raw_byte)
	if(ser.inWaiting()<=0):
		if(currentPacket.pushRawBytes(byte_buffer)):
			print "Received packet:\n",currentPacket
			packets.append(currentPacket)
			currentPacket = xbp.XbeePacket(True)

		byte_buffer = []


