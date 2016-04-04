
#import collections
#import time
#from datetime import datetime

import os
#import os.path
#import zipfile

import h5py
import numpy as np
#import scipy as sp
from scipy import interpolate

#from CalibrationData import CalibrationData
#from CalibrationFile import CalibrationFile
from CalibrationFileReader import CalibrationFileReader
from RawFileReader import RawFileReader
from HDFRoot import HDFRoot
from HDFGroup import HDFGroup
from HDFDataset import HDFDataset


def main():

    root = HDFRoot()

    print("ReadCalibrationFile")
    calibrationMap = CalibrationFileReader.read("cal2013.sip")
    print("calibrationMap:", list(calibrationMap.keys()))
    
    print("ProcessL1a")
    #root = RawFileReader.readRawFile("data.raw", calibrationMap)
    #generateContext(root)
    #print("HDFFile:")
    #root.prnt()
    root = root.processL1a(calibrationMap)
    root.writeHDF5("data_L1a.hdf")
    if os.path.exists("data_L1a.hdf4"):
        os.remove("data_L1a.hdf4")
    root.writeHDF4("data_L1a.hdf4")
    root = HDFRoot.readHDF5("data_L1a.hdf")
    #print("HDFFile:")
    #root.prnt()


    print("ProcessL1b")
    root = root.processL1b(calibrationMap)
    root.writeHDF5("data_L1b.hdf")


    print("ProcessL2")
    root = HDFRoot.readHDF5("data_L1b.hdf")
    #root.processTIMER()
    root = root.processL2()
    root.writeHDF5("data_L2.hdf")
    root = HDFRoot.readHDF5("data_L2.hdf")


    print("ProcessL2s")
    #processGPSTime(root)
    root = root.processL2s()
    #root.prnt()
    root.writeHDF5("data_L2s.hdf")
    root = HDFRoot.readHDF5("data_L2s.hdf")

    print("ProcessL3a")
    root = root.processL3a()
    root.writeHDF5("data_L3a.hdf")
    root = HDFRoot.readHDF5("data_L3a.hdf")


if __name__ == "__main__":
    main()
