import test_configuration as tc
#from xbeeframework import XBeeReader as xbr
import xbeeframework.XBeeReader as xbr
from xbeeframework import XBeeConnection as xbc
from xbeeframework import XBeePacketHandler as xbph
from xbeeframework import XBeeFrameDatabase as xbfdb
import traceback
import logging


def packetCallback(packet, env = {}):
    print "New packet recieved: " + str(packet)


conn = xbc.XBeeConnection()

# create a logger object
framework_log = logging.getLogger("messages")
m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
m_log_file = logging.FileHandler(tc.configuration['logFile'])
m_log_file.setFormatter(m_formatter)
m_streamHandler = logging.StreamHandler()
framework_log.addHandler(m_log_file)
framework_log.addHandler(m_streamHandler)
framework_log.setLevel(logging.DEBUG)

framework_log.info("XBeeFramework Start")

try:
    conn.open(tc.configuration["commPort"])
    logString = "Successfully opened COMM port : " \
        + tc.configuration["commPort"]
    framework_log.info(logString)

    # initialize the frame database
    print "Initializing frame database..."
    frameDB = xbfdb.XBeeFrameDatabase()
    frameDB.setLogger(framework_log)
    frameDB.read(tc.configuration["dbFilename"])

    # create our reader
    print "Initializing reader..."
    reader = xbr.XBeeReader()
    reader.setLogger(framework_log)

    # create our packet handler
    handler = xbph.XBeePacketHandler()
    handler.setLogger(framework_log)
    handler.setDatabase(frameDB)

    logString = "Successfully read database: " \
        + tc.configuration["dbFilename"]
    framework_log.info(logString)

    reader.setConnection(conn)
    reader.setHandler(handler)
    reader.setPacketCallback(packetCallback)
    reader.read(True)

except Exception, e:
    logString = "ERROR: " + str(e)
    framework_log.critical(logString)
else:
    pass
finally:
    conn.close()
