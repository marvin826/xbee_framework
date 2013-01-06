import json

directory = "j:\\Users\\Todd\\Projects\\ZigBee\\XBee Framework\data\\"
file_name = "XBee_API_Frame_Database.db"
f = open(directory + file_name, "r")
js = json.load(f)
for key in js.keys():
    print key
