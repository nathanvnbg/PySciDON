
import collections
import json
import os
import shutil

class ConfigFile:
    filename = ""
    settings = collections.OrderedDict()

    @staticmethod
    def printd():
        print("ConfigFile - Printd")
        print("fL0LonMin", ConfigFile.settings["fL0LonMin"])
        print("fL0LonMax", ConfigFile.settings["fL0LonMax"])
        print("cL0Direction", ConfigFile.settings["cL0Direction"])
        print("bL0CleanSunAngle", ConfigFile.settings["bL0CleanSunAngle"])
        print("bL0CleanRotatorAngle", ConfigFile.settings["bL0CleanRotatorAngle"])
        print("fL0SunAngleMin", ConfigFile.settings["fL0SunAngleMin"])
        print("fL0SunAngleMax", ConfigFile.settings["fL0SunAngleMax"])
        print("fL0RotatorAngleMin", ConfigFile.settings["fL0RotatorAngleMin"])
        print("fL0RotatorAngleMax", ConfigFile.settings["fL0RotatorAngleMax"])
        print("fL0RotatorHomeAngle", ConfigFile.settings["fL0RotatorHomeAngle"])
        print("fL0RotatorDelay", ConfigFile.settings["fL0RotatorDelay"])
        print("bL0SplitRawFile", ConfigFile.settings["bL0SplitRawFile"])

        print("fL3aInterpInterval", ConfigFile.settings["fL3aInterpInterval"])

        print("fL4TimeInterval", ConfigFile.settings["fL4TimeInterval"])
        print("bL4EnableQualityFlags", ConfigFile.settings["bL4EnableQualityFlags"])
        print("fL4SignificantEsFlag", ConfigFile.settings["fL4SignificantEsFlag"])
        print("fL4DawnDuskFlag", ConfigFile.settings["fL4DawnDuskFlag"])
        print("fL4RainfallHumidityFlag", ConfigFile.settings["fL4RainfallHumidityFlag"])
        print("fL4DefaultWindSpeed", ConfigFile.settings["fL4DefaultWindSpeed"])
        print("fL4RhoSky", ConfigFile.settings["fL4RhoSky"])
        print("bL4PerformNIRCorrection", ConfigFile.settings["bL4PerformNIRCorrection"])
        print("fL4PercentLt", ConfigFile.settings["fL4PercentLt"])


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

        ConfigFile.settings["bL0CheckCoords"] = 0
        ConfigFile.settings["fL0LonMin"] = 0.0
        ConfigFile.settings["fL0LonMax"] = 0.0
        ConfigFile.settings["cL0Direction"] = 'E'
        ConfigFile.settings["bL0CleanSunAngle"] = 0
        ConfigFile.settings["bL0CleanRotatorAngle"] = 0
        ConfigFile.settings["fL0SunAngleMin"] = 90.0
        ConfigFile.settings["fL0SunAngleMax"] = 135.0
        ConfigFile.settings["fL0RotatorAngleMin"] = -40.0
        ConfigFile.settings["fL0RotatorAngleMax"] = 40.0
        ConfigFile.settings["fL0RotatorHomeAngle"] = 0.0
        ConfigFile.settings["fL0RotatorDelay"] = 60.0
        ConfigFile.settings["bL0SplitRawFile"] = 0

        ConfigFile.settings["fL3aInterpInterval"] = 1.0

        ConfigFile.settings["fL4TimeInterval"] = 60
        ConfigFile.settings["bL4EnableQualityFlags"] = 1
        ConfigFile.settings["fL4SignificantEsFlag"] = 2.0
        ConfigFile.settings["fL4DawnDuskFlag"] = 1.0
        ConfigFile.settings["fL4RainfallHumidityFlag"] = 1.095
        ConfigFile.settings["fL4DefaultWindSpeed"] = 0.0
        ConfigFile.settings["fL4RhoSky"] = 0.0
        ConfigFile.settings["bL4PerformNIRCorrection"] = 0
        ConfigFile.settings["fL4PercentLt"] = 5

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
        configPath = os.path.join("Config", filename)
        if os.path.isfile(configPath):
            ConfigFile.filename = filename
            text = ""
            with open(configPath, 'r') as f:
                text = f.read()
                ConfigFile.settings = json.loads(text, object_pairs_hook=collections.OrderedDict)
                ConfigFile.createCalibrationFolder()


    # Deletes a config
    @staticmethod
    def deleteConfig(filename):
        print("ConfigFile - Delete Config")
        configPath = os.path.join("Config", filename)
        if os.path.isfile(configPath):
            ConfigFile.filename = filename
            calibrationPath = ConfigFile.getCalibrationDirectory()
            os.remove(configPath)
            shutil.rmtree(calibrationPath)
        

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

