
import collections
import csv
import os
#import sys

import h5py
import numpy as np
#import scipy as sp

from CSVWriter import CSVWriter
from CalibrationFileReader import CalibrationFileReader
#from RawFileReader import RawFileReader
from HDFRoot import HDFRoot
#from HDFGroup import HDFGroup
#from HDFDataset import HDFDataset

from config import settings
from Utilities import Utilities
from WindSpeedReader import WindSpeedReader

from PreprocessRawFile import PreprocessRawFile
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
    def preprocessData(preprocessDirectory, dataDirectory, calibrationMap, checkCoords, startLongitude, endLongitude, direction, doCleaning, angleMin, angleMax):
        PreprocessRawFile.processDirectory(preprocessDirectory, dataDirectory, calibrationMap, checkCoords, startLongitude, endLongitude, direction, doCleaning, angleMin, angleMax)

    # Read wind speed file
    @staticmethod
    def processWindData(fp):
        windDirectory = settings["sWindSpeedFolder"].strip('"')
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(windDirectory, filename + ".csv")

        if not os.path.isfile(filepath):
            return None

        #filepath = "WindSpeed/BritishColumbiaFerries_HorseshoeBay-DepartureBay_WindMonitoringSysteWindSpeed_20160727T223014Z_20160727T232654Z-NaN_clean.csv"
        #windSpeedData = WindSpeedReader.readWindSpeed(filepath)
        windSpeedData = WindSpeedReader.readWindSpeed(filepath)
        
        return windSpeedData


    @staticmethod
    def processL1a(fp, calibrationMap):
        (dirpath, filename) = os.path.split(fp)
        name = os.path.splitext(filename)[0]
        
        # Create "L0" file to save program start time
        #nm = os.path.join(dirpath, name + "_L0.txt")
        #f = open(nm, 'w')
        
        filepath = os.path.join(dirpath, filename)
        if not os.path.isfile(filepath):
            return None
        print("ProcessL1a")
        root = ProcessL1a.processL1a(calibrationMap, filepath)
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, name + "_L1a.hdf"))

    @staticmethod
    def processL1b(fp, calibrationMap):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L1a.hdf")
        if not os.path.isfile(filepath):
            return None
        print("ProcessL1b")
        root = HDFRoot.readHDF5(filepath)
        #print("HDFFile:")
        #root.printd()
        root = ProcessL1b.processL1b(root, calibrationMap)
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L1b.hdf"))

    @staticmethod
    def processL2(fp):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L1b.hdf")
        if not os.path.isfile(filepath):
            return None
        print("ProcessL2")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL2.processL2(root)
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L2.hdf"))

    @staticmethod
    def processL2s(fp):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L2.hdf")
        if not os.path.isfile(filepath):
            return None
        print("ProcessL2s")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL2s.processL2s(root)
        #root.printd()
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L2s.hdf"))

    @staticmethod
    def processL3a(fp):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L2s.hdf")
        if not os.path.isfile(filepath):
            return None
        print("ProcessL3a")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL3a.processL3a(root)
        if root is not None:
            root.writeHDF5(os.path.join(dirpath, filename + "_L3a.hdf"))

    @staticmethod
    def processL4(fp, windSpeedData):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L3a.hdf")
        if not os.path.isfile(filepath):
            return None
        print("ProcessL4")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL4.processL4(root, windSpeedData)
        #root = ProcessL4a.processL4a(root)
        if root is not None:
            Utilities.plotReflectance(root, filename)
            root.writeHDF5(os.path.join(dirpath, filename + "_L4.hdf"))



    # Saving data to formatted csv file
    @staticmethod
    def outputCSV_L4(fp):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]

        filepath = os.path.join(dirpath, filename + "_L4.hdf")
        if not os.path.isfile(filepath):
            return

        root = HDFRoot.readHDF5(filepath)
        if root is None:
            print("outputCSV: root is None")
            return

        Controller.outputCSV(fp, root, "Reflectance", "ES")
        Controller.outputCSV(fp, root, "Reflectance", "LI")
        Controller.outputCSV(fp, root, "Reflectance", "LT")
        Controller.outputCSV(fp, root, "Reflectance", "Rrs")


    @staticmethod
    def outputCSV(fp, root, gpName, dsName):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]

        gp = root.getGroup(gpName)
        ds = gp.getDataset(dsName)
        #np.savetxt('Data/test.out', ds.data)

        if not ds:
            print("Warning - outputCSV: missing dataset")
            return

        dirpath = "csv"
        name = filename[28:43]

        outList = []
        columnName = dsName.lower()

        total = ds.data.shape[0]
        #ls = ["wl"] + [k for k,v in sorted(ds.data.dtype.fields.items(), key=lambda k: k[1])]
        ls = ["wl"] + list(ds.data.dtype.names)
        outList.append(ls)
        for i in range(total):
            n = str(i+1)
            ls = [columnName + "_" + name + '_' + n] + ['%f' % num for num in ds.data[i]]
            outList.append(ls)

        outList = zip(*outList)

        filename = dsName.upper() + "_" + name
        #filename = name + "_" + dsName.upper()
        csvPath = os.path.join(dirpath, filename + ".csv")

        with open(csvPath, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(outList)


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
        #Controller.outputCSV_L4(fp)
        #CSVWriter.outputTXT_L1a(fp)   
        #CSVWriter.outputTXT_L1b(fp)
        #CSVWriter.outputTXT_L2(fp)
        #CSVWriter.outputTXT_L2s(fp)
        #CSVWriter.outputTXT_L3a(fp)
        #CSVWriter.outputTXT_L4(fp)
        #root = HDFRoot.readHDF5(os.path.join(dirpath, filename + "_L3a.hdf"))


    @staticmethod
    def processMultiLevel(fp, calibrationMap, level=4):
        print("Processing: " + fp)
        Controller.processL1a(fp, calibrationMap)
        Controller.processL1b(fp, calibrationMap)
        #if level >= 1:
        Controller.processL2(fp)
        if level >= 2:
            Controller.processL2s(fp)
        if level >= 3:
            Controller.processL3a(fp)
        if level >= 4:
            windSpeedData = Controller.processWindData(fp)
            Controller.processL4(fp, windSpeedData)
            #Controller.outputCSV_L4(fp)
        CSVWriter.outputTXT_L1a(fp)   
        CSVWriter.outputTXT_L1b(fp)
        CSVWriter.outputTXT_L2(fp)
        CSVWriter.outputTXT_L2s(fp)
        CSVWriter.outputTXT_L3a(fp)
        CSVWriter.outputTXT_L4(fp)
        print("Processing: " + fp + " - DONE")


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
    def processDirectory(path, calibrationMap, level=4):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for name in sorted(filenames):
                #print("infile:", name)
                if os.path.splitext(name)[1].lower() == ".raw":
                    #Controller.processAll(os.path.join(dirpath, name), calibrationMap)
                    Controller.processMultiLevel(os.path.join(dirpath, name), calibrationMap, level)
            break

    # Used to process every file in a list of files
    @staticmethod
    def processFilesMultiLevel(files, calibrationMap, level=4):
        print("processFilesMultiLevel")
        for fp in files:
            print("Processing: " + fp)
            Controller.processMultiLevel(fp, calibrationMap, level)
        print("processFilesMultiLevel - DONE")


