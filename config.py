
import configparser

config = configparser.ConfigParser()
config.read("Config.ini")
#print(config.sections())
#print(config["MainSettings"]["sPreprocessFolder"])
settings = config["MainSettings"]
#print(settings["sCalibrationFolder"])
