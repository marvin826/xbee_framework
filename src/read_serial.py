import XBeeReader as xbr
import XBeeConnection as xbc
import XBeePacketHandler as xbph


conn = xbc.XBeeConnection()

try:
    conn.open("COM6")
    print "Successfully opened COMM port"

    reader = xbr.XBeeReader()
    handler = xbph.XBeePacketHandler()

    reader.setConnection(conn)
    reader.setHandler(handler)
    reader.read(True)

except Exception, e:
    print "ERROR: ", e
else:
    pass
finally:
    conn.close()
