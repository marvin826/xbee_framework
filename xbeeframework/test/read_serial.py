import XBeeReader as xbr
import XBeeConnection as xbc
import XBeePacketHandler as xbph
import XBeeFrameDatabase as xbfdb
import traceback
import logging

configuration = {
    "dbFilename": "j:\\Users\\Todd\\Projects\\ZigBee\\XBee Framework"
    + "\\data\\XBee_API_Frame_Database.db",
    "commPort": "COM6",
    "logFile": "j:\\Users\\Todd\\Projects\\ZigBee\\XBee Framework"
    + "\\XBeeFramework.log"

}


def packetCallback(jsonStr):
    print "New packet recieved: " + jsonStr


conn = xbc.XBeeConnection()

# create a logger object
framework_log = logging.getLogger("messages")
m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
m_log_file = logging.FileHandler(configuration['logFile'])
m_log_file.setFormatter(m_formatter)
m_streamHandler = logging.StreamHandler()
framework_log.addHandler(m_log_file)
framework_log.addHandler(m_streamHandler)
framework_log.setLevel(logging.INFO)

framework_log.info("XBeeFramework Start")

try:
    conn.open(configuration["commPort"])
    logString = "Successfully opened COMM port : " \
        + configuration["commPort"]
    framework_log.info(logString)

    # initialize the frame database
    frameDB = xbfdb.XBeeFrameDatabase()
    frameDB.read(configuration["dbFilename"])

    # create our reader
    reader = xbr.XBeeReader()
    reader.setLogger(framework_log)

    # create our packet handler
    handler = xbph.XBeePacketHandler()
    handler.setLogger(framework_logq)
    handler.setDatabase(frameDB)

    logString = "Successfully read database: " \
        + configuration["dbFilename"]
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
