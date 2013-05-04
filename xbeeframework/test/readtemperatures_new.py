import test_configuration as tc
import XBeeReader as xbr
import XBeeConnection as xbc
import XBeePacketHandler as xbph
import XBeeFrameDatabase as xbfdb
import time
import twitter
import logging

CONSUMER_KEY = "bx0cYPrSAjH7nx67nkws5Q"
CONSUMER_SECRET = "oiZaiSAcoY2VPSw2tCwL9Jm89I63dF6tDUtgT5SZSA"
ACCESS_TOKEN = "558113021-HFyFIeMXJb3T2jK6S8U8ZSNkf66YBIrwBASp95I3"
ACCESS_TOKEN_SECRET = "rk9lE9lZgTFfuYW6d8M3Xtaj9SKbnd38PBrZGEXDpYE"


def createMessageLog():

    message_log = logging.getLogger("messages")
    m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    m_log_file = logging.FileHandler('app_messages.log')
    m_log_file.setFormatter(m_formatter)
    m_streamHandler = logging.StreamHandler()
    message_log.addHandler(m_log_file)
    message_log.addHandler(m_streamHandler)
    message_log.setLevel(logging.DEBUG)

    return message_log


def createTemperatureLog():

    temperature_log = logging.getLogger("temperatures")
    t_log_file = logging.FileHandler("temperatures.csv")
    temperature_log.addHandler(t_log_file)
    temperature_log.setLevel(logging.INFO)

    return temperature_log

message_log = createMessageLog()
temperature_log = createTemperatureLog()

last_tweet_time = 0
last_light_reading = -1


def packetCallback(packet):

    # check the frame type and make sure it's what we want
    frameType = packet["FrameType"]
    message_log.debug(packet)

    if(frameType == '0x92'):

        updateTime = time.localtime()

        comps = packet["Components"]
        packetTime = packet["TimeStamp"]
        analog_values = comps["Analog Samples"]["values"]

        lightReading = analog_values["AD1"]
        message_log.debug("light raw: " + str(lightReading))
        rTempReading = analog_values["AD0"]
        message_log.debug("temp raw: " + str(rTempReading))
        rVoltage = analog_values["Supply Voltage"]
        message_log.debug("supply raw: " + str(rVoltage))

        tempReading = (rTempReading * 1200.0) / 1023.0
        tempReading = (tempReading - 500.0) / 10.0
        tempReading = ((tempReading * 9.0) / 5.0) + 32.0
        message_log.debug("temperature (F): " + str(tempReading))

        supplyVoltage = (rVoltage * 1200.0) / 1023.0
        supplyVoltage = supplyVoltage / 1000.0
        message_log.debug("supply voltage (V): " + str(supplyVoltage))

        tempLogMessage = "{0},{1},{2},{3}"
        tempLogMessage.format(packetTime,
                              tempReading,
                              supplyVoltage,
                              lightReading)
        temperature_log.info(tempLogMessage)

        curr_epoch_time = time.mktime(updateTime)
        if(curr_epoch_time - last_tweet_time > 1800):
            last_tweet_time = curr_epoch_time
            tweet = "Current temp from Aurora: {0} degrees ({1})"
            tweet.format(tempReading, supplyVoltage)
            api.PostUpdate(tweet)

        # tweet sunrise/sunset
        if(light > 0 and last_light_reading == 0):  # sunrise
            tweet = "Good morning! Sunrise at {0}"
            tweet.format(packetTime)
            api.PostUpdate(tweet)
        if(light == 0 and last_light_reading > 0):  # sunset
            tweet = "Good night! Sunset at {0}"
            tweet.format(packetTime)
            api.PostUpdate(tweet)
        last_light_reading = lightReading


def read_temperatures():

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

    conn = xbc.XBeeConnection()

    try:
        conn.open(tc.configuration["commPort"])
        logString = "Successfully opened COMM port : " \
                    + tc.configuration["commPort"]
        message_log.info(logString)

        # initialize the frame database
        frameDB = xbfdb.XBeeFrameDatabase()
        frameDB.read(tc.configuration["dbFilename"])

        # create our reader
        reader = xbr.XBeeReader()
        reader.setLogger(message_log)

        # create our packet handler
        handler = xbph.XBeePacketHandler()
        handler.setLogger(message_log)
        handler.setDatabase(frameDB)

        logString = "Successfully read database: " \
            + tc.configuration["dbFilename"]
        message_log.info(logString)

        reader.setConnection(conn)
        reader.setHandler(handler)
        reader.setPacketCallback(packetCallback)
        reader.read(True)

    except Exception, e:
        logString = "ERROR: " + str(e)
        message_log.critical(logString)
    else:
        pass
    finally:
        conn.close()

read_temperatures()
