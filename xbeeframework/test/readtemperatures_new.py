import test_configuration as tc
from xbeeframework import XBeeReader as xbr
from xbeeframework import XBeeConnection as xbc
from xbeeframework import XBeePacketHandler as xbph
from xbeeframework import XBeeFrameDatabase as xbfdb
import time
import requests
import twitter
import logging
import traceback


environment = {'last_light_reading': -1, 'last_tweet_time': 0}


def createMessageLog():

    message_log = logging.getLogger("messages")
    m_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    m_log_file = logging.FileHandler(tc.configuration['logFile'])
    m_log_file.setFormatter(m_formatter)
    m_streamHandler = logging.StreamHandler()
    message_log.addHandler(m_log_file)
    message_log.addHandler(m_streamHandler)
    message_log.setLevel(logging.INFO)

    return message_log


def createTemperatureLog():

    temperature_log = logging.getLogger("temperatures")
    t_log_file = logging.FileHandler(tc.configuration['temperatureLog'])
    temperature_log.addHandler(t_log_file)
    temperature_log.setLevel(logging.INFO)

    return temperature_log

def createGarageLog():

    garage_log = logging.getLogger("garage")
    g_log_file = logging.FileHandler(tc.configuration['garageLog'])
    garage_log.addHandler(g_log_file)
    garage_log.setLevel(logging.INFO)

    return garage_log

message_log = createMessageLog()
temperature_log = createTemperatureLog()
garage_log = createGarageLog()


def packetCallback(packet, env={}):

    message_log.debug("packetCallback: " + str(packet))
    message_log.debug("env: " + str(env))

    # check the frame type and make sure it's what we want
    frameType = packet["FrameType"]
    address = packet['Components']['64-bit Source Address']['address']

    message_log.debug("received frame type: " + frameType)
    message_log.debug("from address: " + address)
    if(frameType == '0x92' and address == '0013 a200 4086 a3da'):
        handleTemperatureReading(packet, env)
    elif(frameType == '0x92' and address == '0013 a200 4086 9617'):
        handleGarageReading(packet, env)

def handleGarageReading(packet, env):

    updateTime = time.localtime()

    comps = packet["Components"]
    packetTimeStamp = packet["TimeStamp"]
    packetTime = packetTimeStamp.split("T")[1]
    packetDate = packetTimeStamp.split("T")[0]

    analog_values = comps["Analog Samples"]["values"]
    rVoltage = analog_values["Supply Voltage"]
    message_log.debug("supply raw: " + str(rVoltage))
    rTempReading = analog_values["AD2"]
    message_log.debug("temp raw: " + str(rTempReading))

    tempReading = (rTempReading * 1200.0) / 1023.0
    tempReading = (tempReading - 500.0) / 10.0
    tempReading = ((tempReading * 9.0) / 5.0) + 32.0
    message_log.debug("temperature (F): " + str(tempReading))

    supplyVoltage = (rVoltage * 1200.0) / 1023.0
    supplyVoltage = supplyVoltage / 1000.0
    message_log.debug("supply voltage (V): " + str(supplyVoltage))

    digital_values = comps["Digital Samples"]["values"]
    doorA = "Open"
    if(digital_values["AD1/DI O1"]):
        doorA = "Closed"
    doorB = "Open"
    if(digital_values["AD0/DI O0"] ):
        doorB = "Closed"

    garageLogMessage = "{0},{1},{2},{3},{4},{5}"
    garageLogMessage = garageLogMessage.format(packetTime,
                                               packetDate,
                                               tempReading,
                                               doorA,
                                               doorB,
                                               supplyVoltage)
    garage_log.info(garageLogMessage)


def handleTemperatureReading(packet, env):

    updateTime = time.localtime()

    comps = packet["Components"]
    packetTimeStamp = packet["TimeStamp"]
    packetTime = packetTimeStamp.split("T")[1]
    packetDate = packetTimeStamp.split("T")[0]

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

    tempLogMessage = "{0},{1},{2},{3},{4}"
    tempLogMessage = tempLogMessage.format(packetTime,
                                           packetDate,
                                           tempReading,
                                           supplyVoltage,
                                           lightReading)
    temperature_log.info(tempLogMessage)

    last_tweet_time = 0
    if 'last_tweet_time' in env:
        last_tweet_time = env['last_tweet_time']

    last_light_reading = 0
    if 'last_light_reading' in env:
        last_light_reading = env['last_light_reading']

    api = None
    if 'api' in env:
        api = env['api']

    curr_epoch_time = time.mktime(updateTime)
    if(curr_epoch_time - last_tweet_time > 1800):
        env['last_tweet_time'] = curr_epoch_time
        tweet = "Current temp from Aurora: {0:03.2f} degrees " + \
                "({1:03.2f}) {2}"
        tweet = tweet.format(tempReading, supplyVoltage, packetTime)
        message_log.debug(tweet)
        if(api is not None):
            try:
                api.PostUpdate(tweet)
            except requests.exceptions.ConnectionError as e:
                message_log.info(str(e))


    # tweet sunrise/sunset
    if(lightReading > 0 and last_light_reading == 0):  # sunrise
        tweet = "Good morning! Sunrise at {0}"
        tweet = tweet.format(packetTime)
        message_log.debug(tweet)
        if(api is not None):
            try:
                api.PostUpdate(tweet)
            except requests.exceptions.ConnectionError as e:
                message_log.info(str(e))
    if(lightReading == 0 and last_light_reading > 0):  # sunset
        tweet = "Good night! Sunset at {0}"
        tweet = tweet.format(packetTime)
        message_log.debug(tweet)
        if(api is not None):
            try:
                api.PostUpdate(tweet)
            except requests.exceptions.ConnectionError as e:
                message_log.info(str(e))
    env['last_light_reading'] = lightReading


def read_temperatures():

    message_log.info("KaiserWeather::read_temperatures start")

    # initialize twitter account
    try:
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=ACCESS_TOKEN,
                          access_token_secret=ACCESS_TOKEN_SECRET)
        environment['api'] = api
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
        frameDB.setLogger(message_log)
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
        reader.setPacketCallback(packetCallback, environment)
        reader.read(True)

    except Exception, e:
        logString = "readtemperatures_new ERROR: " + str(e)
        traceback.print_exc()
        message_log.critical(logString)
    else:
        
    finally:
            

read_temperatures()
