
import collections
import json
import os

class ConfigFile:
    filename = ""
    settings = collections.OrderedDict()

    @staticmethod
    def printd():
        print("ConfigFile - Printd")
        print("fL0LonMin", ConfigFile.settings["fL0LonMin"])
        print("fL0LonMax", ConfigFile.settings["fL0LonMax"])
        print("cL0Direction", ConfigFile.settings["cL0Direction"])
        print("bL0PerformCleaning", ConfigFile.settings["bL0PerformCleaning"])
        print("fL0AngleMin", ConfigFile.settings["fL0AngleMin"])
        print("fL0AngleMax", ConfigFile.settings["fL0AngleMax"])

        print("fL3aInterpInterval", ConfigFile.settings["fL3aInterpInterval"])

        print("fL4TimeInterval", ConfigFile.settings["fL4TimeInterval"])
        print("bL4EnableQualityFlags", ConfigFile.settings["bL4EnableQualityFlags"])
        print("fL4SignificantEsFlag", ConfigFile.settings["fL4SignificantEsFlag"])
        print("fL4DawnDuskFlag", ConfigFile.settings["fL4DawnDuskFlag"])
        print("fL4RainfallHumidityFlag", ConfigFile.settings["fL4RainfallHumidityFlag"])
        print("fL4DefaultWindSpeed", ConfigFile.settings["fL4DefaultWindSpeed"])
        print("bL4PerformNIRCorrection", ConfigFile.settings["bL4PerformNIRCorrection"])

    # Creates the calibration file folder if not exist
    @staticmethod
    def createCalibrationFolder():
        #print("ConfigFile - createCalibrationFolder")
        fp = ConfigFile.getCalibrationDirectory()
        os.makedirs(fp, exist_ok=True)


    # Generates the default configuration
    @staticmethod
    def createDefaultConfig(name):
        print("ConfigFile - Create Default Config")

        #ConfigFile.settings["CalibrationFiles"] = {'GPRMC_WithMode.tdf': 1, \
        #        'HED527A.cal': 1, 'HLD419A.cal': 1, 'HLD420A.cal': 1, 'HSE527A.cal': 1, \
        #        'HSL419A.cal': 1, 'HSL420A.cal': 1, 'SATMSG.tdf': 1, 'SATNAV0004A.tdf': 1}
        ConfigFile.settings["CalibrationFiles"] = {}

        ConfigFile.settings["bL0CheckCoords"] = 1
        ConfigFile.settings["fL0LonMin"] = 0.0
        ConfigFile.settings["fL0LonMax"] = 0.0
        ConfigFile.settings["cL0Direction"] = 'E'
        ConfigFile.settings["bL0PerformCleaning"] = 1
        ConfigFile.settings["fL0AngleMin"] = 90.0
        ConfigFile.settings["fL0AngleMax"] = 135.0

        ConfigFile.settings["fL3aInterpInterval"] = 1.0

        ConfigFile.settings["fL4TimeInterval"] = 60
        ConfigFile.settings["bL4EnableQualityFlags"] = 1
        ConfigFile.settings["fL4SignificantEsFlag"] = 2.0
        ConfigFile.settings["fL4DawnDuskFlag"] = 1.0
        ConfigFile.settings["fL4RainfallHumidityFlag"] = 1.095
        ConfigFile.settings["fL4DefaultWindSpeed"] = 0.0
        ConfigFile.settings["bL4PerformNIRCorrection"] = 1

        if not name.endswith(".cfg"):
            name = name + ".cfg"
        ConfigFile.filename = name
        ConfigFile.saveConfig(name)


    # Saves the cfg file
    @staticmethod
    def saveConfig(filename):
        print("ConfigFile - Save Config")

        jsn = json.dumps(ConfigFile.settings)
        fp = os.path.join("Config", filename)

        #print(os.path.abspath(os.curdir))
        with open(fp, 'w') as f:
            f.write(jsn)
        ConfigFile.createCalibrationFolder()

    # Loads the cfg file
    # ToDo: Apply default values to any settings that are missing (in case settings are updated)
    @staticmethod
    def loadConfig(filename):
        print("ConfigFile - Load Config")

        ConfigFile.filename = filename

        text = ""
        fp = os.path.join("Config", filename)
        with open(fp, 'r') as f:
            text = f.read()
        ConfigFile.settings = json.loads(text, object_pairs_hook=collections.OrderedDict)
        ConfigFile.createCalibrationFolder()
        #ConfigFile.printd()
        

    @staticmethod
    def getCalibrationDirectory():
        print("ConfigFile - getCalibrationDirectory")
        calibrationDir = os.path.splitext(ConfigFile.filename)[0] + "_Calibration"
        calibrationPath = os.path.join("Config", calibrationDir)
        return calibrationPath

    @staticmethod
    def refreshCalibrationFiles():
        print("ConfigFile - refreshCalibrationFiles")
        calibrationPath = ConfigFile.getCalibrationDirectory()
        files = os.listdir(calibrationPath)

        newCalibrationFiles = {}
        calibrationFiles = ConfigFile.settings["CalibrationFiles"]
        
        for file in files:
            if file in calibrationFiles:
                newCalibrationFiles[file] = calibrationFiles[file]
            else:
                newCalibrationFiles[file] = {"enabled": 0, "frameType": "Not Required"}

        ConfigFile.settings["CalibrationFiles"] = newCalibrationFiles

    @staticmethod
    def setCalibrationConfig(calFileName, enabled, frameType):
        print("ConfigFile - setCalibrationConfig")
        calibrationFiles = ConfigFile.settings["CalibrationFiles"]
        calibrationFiles[calFileName] = {"enabled": enabled, "frameType": frameType}

    @staticmethod
    def getCalibrationConfig(calFileName):
        print("ConfigFile - getCalibrationConfig")
        calibrationFiles = ConfigFile.settings["CalibrationFiles"]
        return calibrationFiles[calFileName]

