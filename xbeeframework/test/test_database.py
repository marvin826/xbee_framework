import XBeeFrameDatabase


directory = "j:\\Users\\Todd\\Projects\\ZigBee\\XBee Framework\data\\"
filename = "XBee_API_Frame_Database.db"
fullpath = directory + filename

xbfdb = XBeeFrameDatabase.XBeeFrameDatabase()

xbfdb.read(fullpath)
print xbfdb
