
from datetime import datetime

import os.path
import zipfile

import h5py
import numpy as np

from CalibrationData import CalibrationData
from CalibrationFile import CalibrationFile
from HDFRoot import HDFRoot
from HDFGroup import HDFGroup
from HDFDataset import HDFDataset

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
                    print("id:", cf.m_id)
                    calibrationMap[cf.m_id] = cf

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
    contextMap["SATHED0150"].m_id = "Reference"
    contextMap["SATHED0150"].m_sensorType = "ES"
    contextMap["SATHED0150"].m_frameType = "ShutterDark"
    contextMap["SATHLD0151"].m_id = "SAS"
    contextMap["SATHLD0151"].m_sensorType = "LI"
    contextMap["SATHLD0151"].m_frameType = "ShutterDark"
    contextMap["SATHLD0152"].m_id = "SAS"
    contextMap["SATHLD0152"].m_sensorType = "LT"
    contextMap["SATHLD0152"].m_frameType = "ShutterDark"
    contextMap["SATHSE0150"].m_id = "Reference"
    contextMap["SATHSE0150"].m_sensorType = "ES"
    contextMap["SATHSE0150"].m_frameType = "ShutterLight"
    contextMap["SATHSL0151"].m_id = "SAS"
    contextMap["SATHSL0151"].m_sensorType = "LI"
    contextMap["SATHSL0151"].m_frameType = "ShutterLight"
    contextMap["SATHSL0152"].m_id = "SAS"
    contextMap["SATHSL0152"].m_sensorType = "LT"
    contextMap["SATHSL0152"].m_frameType = "ShutterLight"
    contextMap["SATSAS0052"].m_id = "SAS"
    contextMap["SATSAS0052"].m_sensorType = "None"
    contextMap["SATSAS0052"].m_frameType = "LightAncCombined"
    contextMap["$GPRMC"].m_id = "GPS"
    contextMap["$GPRMC"].m_sensorType = "None"
    contextMap["$GPRMC"].m_frameType = "None"
    

    root = HDFRoot()
    root.m_id = "/"
    #root.m_attributes.append((b"PROSOFT", "Prosoft"))
    #root.m_attributes.append((b"PROSOFT_INSTRUMENT_CONFIG", "Prosoft"))
    #root.m_attributes.append((b"PROSOFT_PARAMETERS_FILE_NAME", "Prosoft"))
    #root.m_attributes.append((b"CAL_FILE_NAMES", "Prosoft"))
    #root.m_attributes.append((b"WAVELENGTH_UNITS", "nm"))
    #root.m_attributes.append((b"LU_UNITS", "count"))
    #root.m_attributes.append((b"ED_UNITS", "count"))
    #root.m_attributes.append((b"ES_UNITS", "count"))
    root.m_attributes["RAW_FILE_NAME"] = "data.raw"
    
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
                    root.m_attributes[k] = v
                    
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
                            if len(gp.m_attributes) == 0:
                                gp.m_id += "_" + key
                                gp.m_attributes["CalFileName"] = calibrationMap[key].m_name
                                gp.m_attributes["FrameTag"] = key

                            #cf = calibrationMap[key.lower()]
                            cf = calibrationMap[key]
                            num = cf.convertRaw(b, gp)
                            fp.read(num)

                            i = 32
                            break
                    if i == 32:
                        break

    root.m_attributes["PROCESSING_LEVEL"] = "1a"
    dt = datetime.now()
    dtstr = dt.strftime("%d-%b-%Y %H:%M:%S")
    root.m_attributes["FILE_CREATION_TIME"] = dtstr

    root.m_groups.append(contextMap["SATHED0150"])
    root.m_groups.append(contextMap["SATHLD0151"])
    root.m_groups.append(contextMap["SATHLD0152"])
    root.m_groups.append(contextMap["SATHSE0150"])
    root.m_groups.append(contextMap["SATHSL0151"])
    root.m_groups.append(contextMap["SATHSL0152"])
    root.m_groups.append(contextMap["SATSAS0052"])
    root.m_groups.append(contextMap["$GPRMC"])
    return root


def readHDFFile(filepath):
    root = HDFRoot()
    with h5py.File(filepath, "r") as hf:
        root.read(hf)
    return root

def writeHDFFile(filepath, root):
    with h5py.File(filepath, "w") as hf:
        root.write(hf)

        
def processL1a(root, calibrationMap):
    for gp in root.m_groups:
        cf = calibrationMap[gp.m_attributes["FrameTag"]]
        #print(gp.m_id, gp.m_attributes)
        print("File:", cf.m_id)
        gp.processL1a(cf)
        
        
def lerp(x, xa, xb, ya, yb):
    return (ya + (yb - ya) * (x - xa) / (xb - xa))

def processDarkColumn(y, darkData, darkTimer, lightTimer, newDarkData):
    #print(darkTimer.m_data)
    dt0 = darkTimer.m_data[0,0]
    dtMax = darkTimer.m_data[darkTimer.m_data.shape[0]-1,0]
    for x in range(lightTimer.m_data.shape[0]):
        lt = lightTimer.m_data[x,0]
        #print(lightTimer.m_data[x,0])
        if lt < dt0:
            newDarkData[x,y] = darkData.m_data[0,y]
        elif lt > dtMax:
            newDarkData[x,y] = darkData.m_data[darkData.m_data.shape[0]-1,y]
        else:
            for i in range(darkTimer.m_data.shape[0]-1):
                t0 = darkTimer.m_data[i,0]
                t1 = darkTimer.m_data[i+1,0]
                if lt > t0 and lt < t1:
                    d0 = darkData.m_data[i,y]
                    d1 = darkData.m_data[i+1,y]
                    newDarkData[x,y] = lerp(lt, t0, t1, d0, d1)
                    break
        
    #for x in range(darkTimer.m_data.shape[0]):
    #    print(darkTimer.m_data[x,y])
    # less than light timer [0]
    # between light timer [0] and [max]
    # greater than light timer [max]


def processDarkCorrection(root, sensorType):
    darkData = None
    darkTimer = None
    lightData = None
    lightTimer = None
    
    for gp in root.m_groups:
        if gp.m_frameType == "ShutterDark" and gp.hasDataset(sensorType):
            darkData = gp.getDataset(sensorType)
            darkTimer = gp.getDataset("TIMER")
            
        if gp.m_frameType == "ShutterLight" and gp.hasDataset(sensorType):
            lightData = gp.getDataset(sensorType)
            lightTimer = gp.getDataset("TIMER")

    if (darkData == None) or (lightData == None):
        print("Dark Correction, dataset not found:", darkData, lightData)

    # Interpolate Dark Dataset to match number of elements as Light Dataset
    print(len(darkData.m_data), len(lightData.m_data))
    print(lightData.m_data)    
    
    newDarkData = np.copy(lightData.m_data)

    for y in range(darkData.m_data.shape[1]):
        processDarkColumn(y, darkData, darkTimer, lightTimer, newDarkData)

    print(lightData.m_data.shape)
    print(newDarkData.shape)
    darkData.m_data = newDarkData

    # Get corrected data by subtract interpolated dark data from light data
    for x in range(lightData.m_data.shape[0]):
        for y in range(lightData.m_data.shape[1]):
            lightData.m_data[x,y] -= newDarkData[x,y]

    print(lightData.m_data)
            

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
