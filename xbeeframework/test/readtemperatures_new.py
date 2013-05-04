import xbeeframework

import serial
import time
import twitter
import logging

configuration = {
    "dbFilename": project_root + "\\data\\XBee_API_Frame_Database.db",
    "commPort": "COM6",
    "logFile": project_root + "\\XBeeFramework.log"

}

CONSUMER_KEY = "bx0cYPrSAjH7nx67nkws5Q"
CONSUMER_SECRET = "oiZaiSAcoY2VPSw2tCwL9Jm89I63dF6tDUtgT5SZSA"
ACCESS_TOKEN = "558113021-HFyFIeMXJb3T2jK6S8U8ZSNkf66YBIrwBASp95I3"
ACCESS_TOKEN_SECRET = "rk9lE9lZgTFfuYW6d8M3Xtaj9SKbnd38PBrZGEXDpYE"


mPort = "COM4"


def createMessageLog():

    message_log = logging.getLogger("messages")
    m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    m_log_file = logging.FileHandler('app_messages.log')
    m_log_file.setFormatter(m_formatter)
    message_log.addHandler(m_log_file)
    message_log.setLevel(logging.DEBUG)

    return message_log


def createTemperatureLog():

    temperature_log = logging.getLogger("temperatures")
    t_log_file = logging.FileHandler("temperatures.csv")
    temperature_log.addHandler(t_log_file)
    temperature_log.setLevel(logging.INFO)

    return temperature_log

def packetCallback():


def read_temperatures():

    message_log = createMessageLog()
    temperature_log = createTemperatureLog()

    message_log.info("KaiserWeather::read_temperatures start")

    # initialize twitter account
    try:
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=ACCESS_TOKEN,
                          access_token_secret=ACCESS_TOKEN_SECRET)
    except twitter.TwitterError as te:
        message_log.critical("Error initializing Twitter API")
        message_log.critical(te)

    last_tweet_time = 0
    last_light_reading = -1

    conn = xbc.XBeeConnection()

    try:
        conn.opentc.configuration["commPort"])
    logString = "Successfully opened COMM port : " \
        + tc.configuration["commPort"]
    framework_log.info(logString)

    # initialize the frame database
    frameDB = xbfdb.XBeeFrameDatabase()
    frameDB.read(tc.configuration["dbFilename"])

    # create our reader
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

