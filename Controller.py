
import csv
import os

from CSVWriter import CSVWriter
from CalibrationFileReader import CalibrationFileReader
#from RawFileReader import RawFileReader
from HDFRoot import HDFRoot
#from HDFGroup import HDFGroup
#from HDFDataset import HDFDataset

from ConfigFile import ConfigFile
from Utilities import Utilities
from WindSpeedReader import WindSpeedReader

from ProcessL1a import ProcessL1a
from ProcessL1b import ProcessL1b
from ProcessL2 import ProcessL2
from ProcessL2s import ProcessL2s
from ProcessL3a import ProcessL3a
from ProcessL4 import ProcessL4
from ProcessL4a import ProcessL4a


class Controller:

    @staticmethod
    def generateContext(calibrationMap):
        for key in calibrationMap:
            cf = calibrationMap[key]
            cf.printd()
            if cf.id.startswith("SATHED"):
                cf.instrumentType = "Reference"
                cf.media = "Air"
                cf.measMode = "Surface"
                cf.frameType = "ShutterDark"
                cf.sensorType = cf.getSensorType()
            elif cf.id.startswith("SATHSE"):
                cf.instrumentType = "Reference"
                cf.media = "Air"
                cf.measMode = "Surface"
                cf.frameType = "ShutterLight"
                cf.sensorType = cf.getSensorType()
            elif cf.id.startswith("SATHLD"):
                cf.instrumentType = "SAS"
                cf.media = "Air"
                cf.measMode = "VesselBorne"
                cf.frameType = "ShutterDark"
                cf.sensorType = cf.getSensorType()
            elif cf.id.startswith("SATHSL"):
                cf.instrumentType = "SAS"
                cf.media = "Air"
                cf.measMode = "VesselBorne"
                cf.frameType = "ShutterLight"
                cf.sensorType = cf.getSensorType()
            elif cf.id.startswith("$GPRMC"):
                cf.instrumentType = "GPS"
                cf.media = "Not Required"
                cf.measMode = "Not Required"
                cf.frameType = "Not Required"
                cf.sensorType = cf.getSensorType()
            else:
                cf.instrumentType = "SAS"
                cf.media = "Air"
                cf.measMode = "VesselBorne"
                cf.frameType = "LightAncCombined"
                cf.sensorType = cf.getSensorType()


    @staticmethod
    def processCalibration(calPath):
        print("processCalibration")
        print("ReadCalibrationFile ", calPath)
        calibrationMap = CalibrationFileReader.read(calPath)
        #calibrationMap = CalibrationFileReader.readSip("cal2013.sip")
        print("calibrationMap:", list(calibrationMap.keys()))
        Controller.generateContext(calibrationMap)
        print("processCalibration - DONE")
        return calibrationMap

    @staticmethod
    def processCalibrationConfig(configName, calFiles):
        print("processCalibrationConfig")
        calFolder = os.path.splitext(configName)[0] + "_Calibration"
        calPath = os.path.join("Config", calFolder)
        print("ReadCalibrationFile ", calPath)
        calibrationMap = CalibrationFileReader.read(calPath)
        #calibrationMap = CalibrationFileReader.readSip("cal2013.sip")
        #print("calibrationMap:", list(calibrationMap.keys()))
        Controller.generateContext(calibrationMap)

        # Settings from Config file
        print("Apply ConfigFile settings")
        print("calibrationMap keys:", calibrationMap.keys())
        print("config keys:", calFiles.keys())
        for key in list(calibrationMap.keys()):
            #print(key)
            if key in calFiles.keys():
                if calFiles[key]["enabled"]:
                    calibrationMap[key].frameType = calFiles[key]["frameType"]
                else:
                    del calibrationMap[key]
            else:
                del calibrationMap[key]
        print("calibrationMap keys 2:", calibrationMap.keys())
        print("processCalibrationConfig - DONE")
        return calibrationMap

    # Read wind speed file
    @staticmethod
    def processWindData(fp):
        if fp is None:
            return None
        if not os.path.isfile(fp):
            return None
        windSpeedData = WindSpeedReader.readWindSpeed(fp)
        return windSpeedData


    @staticmethod
    def processL1a(fp, calibrationMap):
        # Get input filepath
        (dirpath, filename) = os.path.split(fp)
        name = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename)
        if not os.path.isfile(filepath):
            return None

        # Process the data
        print("ProcessL1a")
        root = ProcessL1a.processL1a(calibrationMap, filepath)

        # Write output file
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, name + "_L1a.hdf"))

    @staticmethod
    def processL1b(fp, calibrationMap):
        # Get input filepath
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L1a.hdf")
        if not os.path.isfile(filepath):
            return None

        # Process the data
        print("ProcessL1b")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL1b.processL1b(root, calibrationMap)

        # Write output file
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L1b.hdf"))

    @staticmethod
    def processL2(fp):
        # Get input filepath
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L1b.hdf")
        if not os.path.isfile(filepath):
            return None

        # Process the data
        print("ProcessL2")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL2.processL2(root)

        # Write output file
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L2.hdf"))

    @staticmethod
    def processL2s(fp):
        # Get input filepath
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L2.hdf")
        if not os.path.isfile(filepath):
            return None

        # Process the data
        print("ProcessL2s")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL2s.processL2s(root)
        #root.printd()

        # Write output file
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L2s.hdf"))

    @staticmethod
    def processL3a(fp):
        # Get input filepath
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L2s.hdf")
        if not os.path.isfile(filepath):
            return None

        # Process the data
        print("ProcessL3a")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL3a.processL3a(root)

        # Write output file
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L3a.hdf"))

    @staticmethod
    def processL4(fp, windSpeedData):
        # Get input filepath
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L3a.hdf")
        if not os.path.isfile(filepath):
            return None

        # Process the data
        print("ProcessL4")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL4.processL4(root, False, windSpeedData)
        root = ProcessL4a.processL4a(root)

        # Write output file
        if root is not None:
            Utilities.plotReflectance(root, dirpath, filename)
            root.writeHDF5(os.path.join(dirpath, filename + "_L4.hdf"))

        # Write to separate file if quality flags are enabled
        enableQualityFlags = int(ConfigFile.settings["bL4EnableQualityFlags"])
        if enableQualityFlags:
            root = HDFRoot.readHDF5(filepath)
            root = ProcessL4.processL4(root, True, windSpeedData)
            root = ProcessL4a.processL4a(root)
            if root is not None:
                Utilities.plotReflectance(root, dirpath, filename + "-flags")
                root.writeHDF5(os.path.join(dirpath, filename + "_L4-flags.hdf"))



    # Process all to level 4 for testing
    @staticmethod
    def processAll(fp, calibrationMap):
        print("Processing: " + fp)
        #Controller.preprocessData(calibrationMap)
        Controller.processL1a(fp, calibrationMap)
        Controller.processL1b(fp, calibrationMap)
        Controller.processL2(fp)
        Controller.processL2s(fp)
        Controller.processL3a(fp)
        windSpeedData = Controller.processWindData(fp)
        Controller.processL4(fp, windSpeedData)
        #CSVWriter.outputTXT_L1a(fp)   
        #CSVWriter.outputTXT_L1b(fp)
        #CSVWriter.outputTXT_L2(fp)
        #CSVWriter.outputTXT_L2s(fp)
        #CSVWriter.outputTXT_L3a(fp)
        #CSVWriter.outputTXT_L4(fp)
        #root = HDFRoot.readHDF5(os.path.join(dirpath, filename + "_L3a.hdf"))


    @staticmethod
    def processSingleLevel(fp, calibrationMap, level, windFile=None):
        print("Process Single Level: " + fp)
        if level == "1a":
            Controller.processL1a(fp, calibrationMap)
        elif level == "1b":
            fp = fp.replace("_L1a.hdf", ".hdf")
            Controller.processL1b(fp, calibrationMap)
        elif level == "2":
            fp = fp.replace("_L1b.hdf", ".hdf")
            Controller.processL2(fp)
        elif level == "2s":
            fp = fp.replace("_L2.hdf", ".hdf")
            Controller.processL2s(fp)
        elif level == "3a":
            fp = fp.replace("_L2s.hdf", ".hdf")
            Controller.processL3a(fp)
        elif level == "4":
            fp = fp.replace("_L3a.hdf", ".hdf")
            windSpeedData = Controller.processWindData(windFile)
            Controller.processL4(fp, windSpeedData)
        print("Output CSV: " + fp)
        CSVWriter.outputTXT_L1a(fp)
        CSVWriter.outputTXT_L1b(fp)
        CSVWriter.outputTXT_L2(fp)
        CSVWriter.outputTXT_L2s(fp)
        CSVWriter.outputTXT_L3a(fp)
        CSVWriter.outputTXT_L4(fp)
        print("Process Single Level: " + fp + " - DONE")


    @staticmethod
    def processMultiLevel(fp, calibrationMap, level=4, windFile=None):
        print("Process Multi Level: " + fp)
        Controller.processL1a(fp, calibrationMap)
        Controller.processL1b(fp, calibrationMap)
        #if level >= 1:
        Controller.processL2(fp)
        if level >= 2:
            Controller.processL2s(fp)
        if level >= 3:
            Controller.processL3a(fp)
        if level >= 4:
            windSpeedData = Controller.processWindData(windFile)
            Controller.processL4(fp, windSpeedData)
        print("Output CSV: " + fp)
        CSVWriter.outputTXT_L1a(fp)
        CSVWriter.outputTXT_L1b(fp)
        CSVWriter.outputTXT_L2(fp)
        CSVWriter.outputTXT_L2s(fp)
        CSVWriter.outputTXT_L3a(fp)
        CSVWriter.outputTXT_L4(fp)
        print("Process Multi Level: " + fp + " - DONE")


    @staticmethod
    def processDirectoryTest(path, calibrationMap, level=4):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for name in sorted(filenames):
                #print("infile:", name)
                if os.path.splitext(name)[1].lower() == ".raw":
                    Controller.processAll(os.path.join(dirpath, name), calibrationMap)
                    #Controller.processMultiLevel(os.path.join(dirpath, name), calibrationMap, level)
            break


    # Used to process every file in the specified directory
    @staticmethod
    def processDirectory(path, calibrationMap, level=4, windFile=None):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for name in sorted(filenames):
                #print("infile:", name)
                if os.path.splitext(name)[1].lower() == ".raw":
                    #Controller.processAll(os.path.join(dirpath, name), calibrationMap)
                    Controller.processMultiLevel(os.path.join(dirpath, name), calibrationMap, level, windFile)
            break

    # Used to process every file in a list of files
    @staticmethod
    def processFilesMultiLevel(files, calibrationMap, level=4, windFile=None):
        print("processFilesMultiLevel")
        for fp in files:
            print("Processing: " + fp)
            Controller.processMultiLevel(fp, calibrationMap, level, windFile)
        print("processFilesMultiLevel - DONE")


    # Used to process every file in a list of files
    @staticmethod
    def processFilesSingleLevel(files, calibrationMap, level, windFile=None):
        print("processFilesSingleLevel")
        for fp in files:
            print("Processing: " + fp)
            Controller.processSingleLevel(fp, calibrationMap, level, windFile)
        print("processFilesSingleLevel - DONE")

