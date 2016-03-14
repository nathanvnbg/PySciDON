
from datetime import datetime

import os.path
import zipfile

import h5py
import numpy as np

from CalibrationData import CalibrationData
from CalibrationFile import CalibrationFile
from HDFGroup import HDFGroup

def readCalibrationFile(fp):
    calibrationMap = {}

    with zipfile.ZipFile(fp, 'r') as zf:
        for finfo in zf.infolist():
            print(finfo.filename)
            if os.path.splitext(finfo.filename)[1].lower() == ".cal" or \
               os.path.splitext(finfo.filename)[1].lower() == ".tdf":
                with zf.open(finfo) as f:
                    cf = CalibrationFile()
                    cf.read(f)
                    print("id:", cf._id)
                    calibrationMap[cf._id] = cf

    return calibrationMap

def readSATHDR(b):
    end = b.find(bytes(b"\x0D\x0A".decode("unicode_escape"), "utf-8"))
    sp1 = b.find(b" ")
    sp2 = b.rfind(b" ")
    str1 = b[sp1+1:sp2].decode("utf-8")
    str2 = b[sp2+2:end-1].decode("utf-8")
    #print(str1, str2)
    if len(str1) == 0:
        str1 = "Missing"
    return (str2, str1)
    

    

def readRawFile(filepath, calibrationMap):

    contextMap = {}


    contextMap["SATHED0150"] = HDFGroup()
    contextMap["SATHLD0151"] = HDFGroup()
    contextMap["SATHLD0152"] = HDFGroup()
    contextMap["SATHSE0150"] = HDFGroup()
    contextMap["SATHSL0151"] = HDFGroup()
    contextMap["SATHSL0152"] = HDFGroup()
    contextMap["SATSAS0052"] = HDFGroup()
    contextMap["$GPRMC"] = HDFGroup()
    contextMap["SATHED0150"]._id = "Reference"
    contextMap["SATHED0150"]._sensorType = "ES"
    contextMap["SATHED0150"]._frameType = "ShutterDark"
    contextMap["SATHLD0151"]._id = "SAS"
    contextMap["SATHLD0151"]._sensorType = "LI"
    contextMap["SATHLD0151"]._frameType = "ShutterDark"
    contextMap["SATHLD0152"]._id = "SAS"
    contextMap["SATHLD0152"]._sensorType = "LT"
    contextMap["SATHLD0152"]._frameType = "ShutterDark"
    contextMap["SATHSE0150"]._id = "Reference"
    contextMap["SATHSE0150"]._sensorType = "ES"
    contextMap["SATHSE0150"]._frameType = "ShutterLight"
    contextMap["SATHSL0151"]._id = "SAS"
    contextMap["SATHSL0151"]._sensorType = "LI"
    contextMap["SATHSL0151"]._frameType = "ShutterLight"
    contextMap["SATHSL0152"]._id = "SAS"
    contextMap["SATHSL0152"]._sensorType = "LT"
    contextMap["SATHSL0152"]._frameType = "ShutterLight"
    contextMap["SATSAS0052"]._id = "SAS"
    contextMap["SATSAS0052"]._sensorType = "None"
    contextMap["SATSAS0052"]._frameType = "LightAncCombined"
    contextMap["$GPRMC"]._id = "GPS"
    contextMap["$GPRMC"]._sensorType = "None"
    contextMap["$GPRMC"]._frameType = "None"
    

    root = HDFGroup()
    root._id = "/"
    #root._attributes.append((b"PROSOFT", "Prosoft"))
    #root._attributes.append((b"PROSOFT_INSTRUMENT_CONFIG", "Prosoft"))
    #root._attributes.append((b"PROSOFT_PARAMETERS_FILE_NAME", "Prosoft"))
    #root._attributes.append((b"CAL_FILE_NAMES", "Prosoft"))
    #root._attributes.append((b"WAVELENGTH_UNITS", "nm"))
    #root._attributes.append((b"LU_UNITS", "count"))
    #root._attributes.append((b"ED_UNITS", "count"))
    #root._attributes.append((b"ES_UNITS", "count"))
    root._attributes["RAW_FILE_NAME"] = "data.raw"
    
    with open(filepath, 'rb') as fp:
        while 1:
            pos = fp.tell()
            b = fp.read(32)
            fp.seek(pos)

            if not b:
                break

            #print b
            for i in range(0, 32):
                testString = b[i:].upper()
                #print("test: ", testString[:6])
            
                if i == 31:
                    fp.read(32)
                    break

                if testString.startswith(b"SATHDR"):
                    #print("SATHDR")
                    if i > 0:
                        fp.read(i)
                    b = fp.read(128)
                    (k,v) = readSATHDR(b)
                    root._attributes[k] = v
                    
                    break
                else:
                    for key in calibrationMap:
                        if testString.startswith(key.upper().encode("utf-8")):
                            if i > 0:
                                fp.read(i)

                            pos = fp.tell()
                            b = fp.read(1024)
                            fp.seek(pos)

                            #gp = contextMap[key.lower()]
                            gp = contextMap[key]
                            if len(gp._attributes) == 0:
                                gp._id += "_" + key
                                gp._attributes["CalFileName"] = calibrationMap[key]._name
                                gp._attributes["FrameTag"] = key

                            #cf = calibrationMap[key.lower()]
                            cf = calibrationMap[key]
                            num = cf.convertRaw(b, gp)
                            fp.read(num)

                            i = 32
                            break
                    if i == 32:
                        break

    root._attributes["PROCESSING_LEVEL"] = "1a"
    dt = datetime.now()
    dtstr = dt.strftime("%d-%b-%Y %H:%M:%S")
    root._attributes["FILE_CREATION_TIME"] = dtstr

    root._groups.append(contextMap["SATHED0150"])
    root._groups.append(contextMap["SATHLD0151"])
    root._groups.append(contextMap["SATHLD0152"])
    root._groups.append(contextMap["SATHSE0150"])
    root._groups.append(contextMap["SATHSL0151"])
    root._groups.append(contextMap["SATHSL0152"])
    root._groups.append(contextMap["SATSAS0052"])
    root._groups.append(contextMap["$GPRMC"])
    return root


def readHDFFile(filepath):
    root = HDFGroup()
    with h5py.File(filepath, "r") as hf:
        root.read(hf)
    return root

def writeHDFFile(filepath, root):
    with h5py.File(filepath, "w") as hf:
        root.write(hf)

        
def processL1a(root, calibrationMap):
    for gp in root._groups:
        cf = calibrationMap[gp._attributes["FrameTag"]]
        #print(gp._id, gp._attributes)
        print("File:", cf._id)
        gp.processL1a(cf)
        
        
def lerp(x, xa, xb, ya, yb):
    return (ya + (yb - ya) * (x - xa) / (xb - xa))

def processDarkColumn(y, darkData, darkTimer, lightTimer, newDarkData):
    #print(darkTimer._data)
    dt0 = darkTimer._data[0,0]
    dtMax = darkTimer._data[darkTimer._data.shape[0]-1,0]
    for x in range(lightTimer._data.shape[0]):
        lt = lightTimer._data[x,0]
        #print(lightTimer._data[x,0])
        if lt < dt0:
            newDarkData[x,y] = darkData._data[0,y]
        elif lt > dtMax:
            newDarkData[x,y] = darkData._data[darkData._data.shape[0]-1,y]
        else:
            for i in range(darkTimer._data.shape[0]-1):
                t0 = darkTimer._data[i,0]
                t1 = darkTimer._data[i+1,0]
                if lt > t0 and lt < t1:
                    d0 = darkData._data[i,y]
                    d1 = darkData._data[i+1,y]
                    newDarkData[x,y] = lerp(lt, t0, t1, d0, d1)
                    break
        
    #for x in range(darkTimer._data.shape[0]):
    #    print(darkTimer._data[x,y])
    # less than light timer [0]
    # between light timer [0] and [max]
    # greater than light timer [max]


def processDarkCorrection(root, sensorType):
    darkData = None
    darkTimer = None
    lightData = None
    lightTimer = None
    
    for gp in root._groups:
        if gp._frameType == "ShutterDark" and gp.hasDataset(sensorType):
            darkData = gp.getDataset(sensorType)
            darkTimer = gp.getDataset("TIMER")
            
        if gp._frameType == "ShutterLight" and gp.hasDataset(sensorType):
            lightData = gp.getDataset(sensorType)
            lightTimer = gp.getDataset("TIMER")

    if (darkData == None) or (lightData == None):
        print("Dark Correction, dataset not found:", darkData, lightData)

    # Interpolate Dark Dataset to match number of elements as Light Dataset
    print(len(darkData._data), len(lightData._data))
    print(lightData._data)    
    
    newDarkData = np.copy(lightData._data)

    for y in range(darkData._data.shape[1]):
        processDarkColumn(y, darkData, darkTimer, lightTimer, newDarkData)

    print(lightData._data.shape)
    print(newDarkData.shape)
    darkData._data = newDarkData

    # Get corrected data by subtract interpolated dark data from light data
    for x in range(lightData._data.shape[0]):
        for y in range(lightData._data.shape[1]):
            lightData._data[x,y] -= newDarkData[x,y]

    print(lightData._data)
            

def main():

    calibrationMap = readCalibrationFile("cal2013.sip")
    print("calibrationMap:", list(calibrationMap.keys()))
    root = readRawFile("data.raw", calibrationMap)
    #print("HDFFile:")
    #root.prnt()
    writeHDFFile("data_1a.hdf", root)
    #root = readHDFFile("data_1a.hdf")
    #print("HDFFile:")
    #root.prnt()
    print("ProcessL1a:")
    processL1a(root, calibrationMap)
    writeHDFFile("data_1b.hdf", root)

    #root = readHDFFile("data_1b.hdf")
    #print("Start Time:", root.getStartTime())
    root.processTIMER()
    #for key in calibrationMap:
    #    print(key)

    processDarkCorrection(root, "ES")
    

if __name__ == "__main__":
    main()
