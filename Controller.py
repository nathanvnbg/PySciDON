
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


class Controller:
    @staticmethod
    def generateContext(calibrationMap):
        for key in calibrationMap:
            cf = calibrationMap[key]
            cf.printd()
            if cf.m_id.startswith("SATHED"):
                cf.m_instrumentType = "Reference"
                cf.m_media = "Air"
                cf.m_measMode = "Surface"
                cf.m_frameType = "ShutterDark"
                cf.m_sensorType = cf.getSensorType()
            elif cf.m_id.startswith("SATHSE"):
                cf.m_instrumentType = "Reference"
                cf.m_media = "Air"
                cf.m_measMode = "Surface"
                cf.m_frameType = "ShutterLight"
                cf.m_sensorType = cf.getSensorType()
            elif cf.m_id.startswith("SATHLD"):
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "ShutterDark"
                cf.m_sensorType = cf.getSensorType()
            elif cf.m_id.startswith("SATHSL"):
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "ShutterLight"
                cf.m_sensorType = cf.getSensorType()
            elif cf.m_id.startswith("$GPRMC"):
                cf.m_instrumentType = "GPS"
                cf.m_media = "Not Required"
                cf.m_measMode = "Not Required"
                cf.m_frameType = "Not Required"
                cf.m_sensorType = cf.getSensorType()
            else:
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "LightAncCombined"
                cf.m_sensorType = cf.getSensorType()


    @staticmethod
    def processCalibration(calPath):
        print("ReadCalibrationFile ", calPath)
        calibrationMap = CalibrationFileReader.read(calPath)
        #calibrationMap = CalibrationFileReader.readSip("cal2013.sip")
        print("calibrationMap:", list(calibrationMap.keys()))
        Controller.generateContext(calibrationMap)
        return calibrationMap

    @staticmethod
    def preprocessData(preprocessDirectory, dataDirectory, calibrationMap, startLongitude, endLongitude, direction):
        PreprocessRawFile.processDirectory(preprocessDirectory, dataDirectory, calibrationMap, startLongitude, endLongitude, direction)

    # Read wind speed file
    @staticmethod
    def processWindData(fp):
        windDirectory = settings["sWindSpeedFolder"].strip('"')
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(windDirectory, filename + ".csv")

        if not os.path.isfile(filepath):
            return None

        #filepath = "WindSpeed/BritishColumbiaFerries_HorseshoeBay-DepartureBay_WindMonitoringSystem_WindSpeed_20160727T223014Z_20160727T232654Z-NaN_clean.csv"
        #windSpeedData = WindSpeedReader.readWindSpeed(filepath)
        windSpeedData = WindSpeedReader.readWindSpeed(filepath)
        
        return windSpeedData


    @staticmethod
    def processL1a(root, fp, calibrationMap):
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
        return root

    @staticmethod
    def processL1b(root, fp, calibrationMap):
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
        return root

    @staticmethod
    def processL2(root, fp):
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
        return root

    @staticmethod
    def processL2s(root, fp):
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
        return root

    @staticmethod
    def processL3a(root, fp):
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
        return root

    @staticmethod
    def processL4(root, fp, windSpeedData):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]
        filepath = os.path.join(dirpath, filename + "_L3a.hdf")
        if not os.path.isfile(filepath):
            return None
        print("ProcessL4")
        root = HDFRoot.readHDF5(filepath)
        root = ProcessL4.processL4(root, windSpeedData)
        if root is not None:
            Utilities.plotReflectance(root, filename)
            root.writeHDF5(os.path.join(dirpath, filename + "_L4.hdf"))
        return root



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
        #np.savetxt('Data/test.out', ds.m_data)

        if not ds:
            print("Warning - outputCSV: missing dataset")
            return

        dirpath = "csv"
        name = filename[28:43]

        outList = []
        columnName = dsName.lower()

        total = ds.m_data.shape[0]
        #ls = ["wl"] + [k for k,v in sorted(ds.m_data.dtype.fields.items(), key=lambda k: k[1])]
        ls = ["wl"] + list(ds.m_data.dtype.names)
        outList.append(ls)
        for i in range(total):
            n = str(i+1)
            ls = [columnName + "_" + name + '_' + n] + ['%f' % num for num in ds.m_data[i]]
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
        root = HDFRoot()
        root = Controller.processL1a(root, fp, calibrationMap)
        root = Controller.processL1b(root, fp, calibrationMap)
        root = Controller.processL2(root, fp)
        root = Controller.processL2s(root, fp)
        root = Controller.processL3a(root, fp)
        windSpeedData = Controller.processWindData(fp)
        root = Controller.processL4(root, fp, windSpeedData)
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
        root = HDFRoot()
        root = Controller.processL1a(root, fp, calibrationMap)
        root = Controller.processL1b(root, fp, calibrationMap)
        #if level >= 1:
        root = Controller.processL2(root, fp)
        if level >= 2:
            root = Controller.processL2s(root, fp)
        if level >= 3:
            root = Controller.processL3a(root, fp)
        if level >= 4:
            windSpeedData = Controller.processWindData(fp)
            root = Controller.processL4(root, fp, windSpeedData)
            #Controller.outputCSV_L4(fp)
        CSVWriter.outputTXT_L1a(fp)   
        CSVWriter.outputTXT_L1b(fp)
        CSVWriter.outputTXT_L2(fp)
        CSVWriter.outputTXT_L2s(fp)
        CSVWriter.outputTXT_L3a(fp)
        CSVWriter.outputTXT_L4(fp)
        print("Processing: " + fp + " - DONE")


    # Used to process every file in the specified directory
    @staticmethod
    def processDirectory(path, calibrationMap, level=4):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for name in sorted(filenames):
                #print("infile:", name)
                if os.path.splitext(name)[1].lower() == ".raw":
                    Controller.processAll(os.path.join(dirpath, name), calibrationMap)
                    #Controller.processMultiLevel(os.path.join(dirpath, name), calibrationMap, level)
            break

    # Used to process every file in a list of files
    @staticmethod
    def processFiles(files, calibrationMap, level=4):
        for fp in files:
            Controller.processMultiLevel(fp, calibrationMap, level)

