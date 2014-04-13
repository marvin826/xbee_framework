import sys

project_root = "/home/kaiserw/application"
sys.path.append(project_root)

configuration = {
    "dbFilename": project_root + "/config/XBee_API_Frame_Database.db",
    "commPort": "/dev/ttyS0",
    "logFile": project_root + "/logs/XBeeFramework.log",
    "temperatureLog" : project_root + "/logs/temperatures.csv",
    "garageLog" : project_root + "/logs/garage_readings.csv"
}
