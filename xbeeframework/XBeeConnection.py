import serial


class XBeeConnection():
    """XBeeConnection manages the serial connection to an XBee radio"""
    def __init__(self):
        self._mSerialPort = None

    def open(self, port, rate=9600):
        # open the serial port to read
        # information
        try:
            self._mSerialPort = serial.Serial(port, rate, timeout=None)
        except serial.serialutil.SerialException as se:
            raise se

    def close(self):
        if(self._mSerialPort):
            self._mSerialPort.close()

    def flushInputBuffer(self):
        if(self._mSerialPort):
            self._mSerialPort.flushInput()

    def getNextByte(self):
        return self._mSerialPort.read(1)

    def moreBytesAvailable(self):
        return (self._mSerialPort.inWaiting() > 0)
