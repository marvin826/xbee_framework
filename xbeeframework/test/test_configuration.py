import sys

project_root = "j:\\Users\\Todd\\Projects\\ZigBee\\XBeeFramework"
sys.path.append(project_root)
sys.path.append(project_root + '\\xbeeframework')

configuration = {
    "dbFilename": project_root + "\\data\\XBee_API_Frame_Database.db",
    "commPort": "COM4",
    "logFile": project_root + "\\XBeeFramework.log"

}
