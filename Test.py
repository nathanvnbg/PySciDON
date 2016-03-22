
import time
from datetime import datetime

import os.path
import zipfile

import h5py
import numpy as np
#import scipy as sp
from scipy import interpolate

from CalibrationData import CalibrationData
from CalibrationFile import CalibrationFile
from HDFRoot import HDFRoot
from HDFGroup import HDFGroup
from HDFDataset import HDFDataset

def readCalibrationFile(fp):
    calibrationMap = {}

    with zipfile.ZipFile(fp, 'r') as zf:
        for finfo in zf.infolist():
            print("infile:", finfo.filename)
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


# ToDo: create more dynamic detection
def generateContext(root):
    for gp in root.m_groups:
        line = gp.m_id[gp.m_id.find("_")+1:]
        #print(line)
        if line == "SATHED0150":
            #gp.m_id = "Reference"
            gp.m_sensorType = "ES"
            gp.m_frameType = "ShutterDark"
        elif line == "SATHLD0151":
            #gp.m_id = "SAS"
            gp.m_sensorType = "LI"
            gp.m_frameType = "ShutterDark"
        elif line == "SATHLD0152":
            #gp.m_id = "SAS"
            gp.m_sensorType = "LT"
            gp.m_frameType = "ShutterDark"
        elif line == "SATHSE0150":
            #gp.m_id = "Reference"
            gp.m_sensorType = "ES"
            gp.m_frameType = "ShutterLight"
        elif line == "SATHSL0151":
            #gp.m_id = "SAS"
            gp.m_sensorType = "LI"
            gp.m_frameType = "ShutterLight"
        elif line == "SATHSL0152":
            #gp.m_id = "SAS"
            gp.m_sensorType = "LT"
            gp.m_frameType = "ShutterLight"
        elif line == "SATSAS0052":
            #gp.m_id = "SAS"
            gp.m_sensorType = "None"
            gp.m_frameType = "LightAncCombined"
        elif line == "GPS":
            #gp.m_id = "GPS"
            gp.m_sensorType = "None"
            gp.m_frameType = "None"


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
    contextMap["SATHLD0151"].m_id = "SAS"
    contextMap["SATHLD0152"].m_id = "SAS"
    contextMap["SATHSE0150"].m_id = "Reference"
    contextMap["SATHSL0151"].m_id = "SAS"
    contextMap["SATHSL0152"].m_id = "SAS"
    contextMap["SATSAS0052"].m_id = "SAS"
    contextMap["$GPRMC"].m_id = "GPS"



    root = HDFRoot()
    root.m_id = "/"
    root.m_attributes["PROSOFT"] = "7.16_6"
    root.m_attributes["PROSOFT_INSTRUMENT_CONFIG"] = "testcfg"
    root.m_attributes["PROSOFT_PARAMETERS_FILE_NAME"] = "test.mat"
    root.m_attributes["CAL_FILE_NAMES"] = "HED150E2013.cal,HLD151C2013.cal," \
        "HLD152C2013.cal,HSE150E2013.cal,HSL151C2013.cal,HSL152C2013.cal," \
        "MPR052a.cal,GPRMC_NoMode.TDF"
    root.m_attributes["WAVELENGTH_UNITS"] = "nm"
    root.m_attributes["LU_UNITS"] = "count"
    root.m_attributes["ED_UNITS"] = "count"
    root.m_attributes["ES_UNITS"] = "count"
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

    root.m_attributes["Head_1"] = "ES 1 1 355.36"
    root.m_attributes["Head_2"] = "ES 1 1 358.66"
    root.m_attributes["Head_3"] = "ES 1 1 361.95"
    root.m_attributes["Head_4"] = "ES 1 1 365.25"
    root.m_attributes["Head_5"] = "ES 1 1 368.54"

    root.m_groups.append(contextMap["SATHED0150"])
    root.m_groups.append(contextMap["SATHLD0151"])
    root.m_groups.append(contextMap["SATHLD0152"])
    root.m_groups.append(contextMap["SATHSE0150"])
    root.m_groups.append(contextMap["SATHSL0151"])
    root.m_groups.append(contextMap["SATHSL0152"])
    root.m_groups.append(contextMap["SATSAS0052"])
    root.m_groups.append(contextMap["$GPRMC"])


    for gp in root.m_groups:
        for ds in gp.m_datasets.values():
            ds.columnsToDataset()

    return root


def readHDFFile(filepath):
    root = HDFRoot()
    with h5py.File(filepath, "r") as hf:
        root.read(hf)
    return root

def writeHDFFile(filepath, root):
    with h5py.File(filepath, "w") as hf:
        root.write(hf)




def utcToSec(utc):
    t = str(int(utc))
    #print(s)
    #print(s[:2], s[2:4], s[4:])
    h = int(t[:2])
    m = int(t[2:4])
    s = int(t[4:])
    return ((h*60)+m)*60+s

def secToTimeTag2(sec):
    #return float(time.strftime("%H%M%S", time.gmtime(sec)))
    t = sec * 1000
    s, ms = divmod(t, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return float("%d%02d%02d%03d" % (h, m, s, ms))

def timeTag2ToSec(time):
    t = str(int(time))
    h = int(t[:2])
    m = int(t[2:4])
    s = int(t[4:6])
    ms = int(t[6:])
    return ((h*60)+m)*60+s+(float(ms)/1000.0)


# recalculate TimeTag2 to follow GPS UTC time
def processGPSTime(root):
    sec = 0

    for gp in root.m_groups:
        if gp.m_id.startswith("GPS"):
            ds = gp.getDataset("UTCPOS")
            sec = utcToSec(ds.m_data["NONE"][0])
            #print("GPS UTCPOS:", ds.m_data["NONE"][0], "-> sec:", sec)
            #print(secToUtc(sec))

    for gp in root.m_groups:
        if not gp.m_id.startswith("GPS"):
            dsTimer = gp.getDataset("TIMER")
            dsTimeTag2 = gp.getDataset("TIMETAG2")
            for x in range(dsTimeTag2.m_data.shape[0]):
                v = dsTimer.m_data["NONE"][x] + sec
                dsTimeTag2.m_data["NONE"][x] = secToTimeTag2(v)


def interpolateSpline(xData, xTimer, yTimer, newXData):
    x = xTimer
    new_x = yTimer

    for k in xData.m_data.dtype.fields.keys():
        y = xData.m_data[k]
        newXData.m_columns[k] = interpolate.interp1d(x, y, kind='cubic', bounds_error=False)(new_x)

        test = False
        for i in range(len(newXData.m_columns[k])):
            if np.isnan(newXData.m_columns[k][i]):
                #print("NaN")
                if test:
                    newXData.m_columns[k][i] = xData.m_data[k][xData.m_data.shape[0]-1]
                else:
                    newXData.m_columns[k][i] = xData.m_data[k][0]
            else:
                test = True


def interpolateLinear(xData, xTimer, yTimer, newXData):
    x = xTimer
    new_x = yTimer

    for k in xData.m_data.dtype.fields.keys():
        y = xData.m_data[k]
        newXData.m_columns[k] = interpolate.interp1d(x, y, kind='linear', bounds_error=False)(new_x)

        test = False
        for i in range(len(newXData.m_columns[k])):
            if np.isnan(newXData.m_columns[k][i]):
                #print("NaN")
                if test:
                    newXData.m_columns[k][i] = xData.m_data[k][xData.m_data.shape[0]-1]
                else:
                    newXData.m_columns[k][i] = xData.m_data[k][0]
            else:
                test = True


# interpolate GPS to match ES using linear interpolation
def interpolateGPSData(node, esGroup, gpsGroup):
    print("Interpolate GPS Data2")

    # ES
    esData = esGroup.getDataset("ES")
    esDateData = esGroup.getDataset("DATETAG")
    esTimeData = esGroup.getDataset("TIMETAG2")

    refGroup = node.getGroup("Reference")
    newESData = refGroup.addDataset("ES_hyperspectral")

    newESData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
    newESData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
    for k in esData.m_data.dtype.fields.keys():
        #print("type",type(esData.m_data[k]))
        newESData.m_columns[k] = esData.m_data[k].tolist()
    newESData.columnsToDataset()


    # GPS
    gpsTimeData = gpsGroup.getDataset("UTCPOS")
    gpsCourseData = gpsGroup.getDataset("COURSE")
    gpsLatPosData = gpsGroup.getDataset("LATPOS")
    gpsLonPosData = gpsGroup.getDataset("LONPOS")
    gpsMagVarData = gpsGroup.getDataset("MAGVAR")
    gpsSpeedData = gpsGroup.getDataset("SPEED")

    gpsGroup = node.getGroup("GPS")
    newGPSCourseData = gpsGroup.addDataset("COURSE")
    newGPSLatPosData = gpsGroup.addDataset("LATPOS")
    newGPSLonPosData = gpsGroup.addDataset("LONPOS")
    newGPSMagVarData = gpsGroup.addDataset("MAGVAR")
    newGPSSpeedData = gpsGroup.addDataset("SPEED")

    newGPSCourseData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
    newGPSCourseData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
    newGPSLatPosData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
    newGPSLatPosData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
    newGPSLonPosData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
    newGPSLonPosData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
    newGPSMagVarData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
    newGPSMagVarData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
    newGPSSpeedData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
    newGPSSpeedData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()


    xTimer = []
    for i in range(gpsTimeData.m_data.shape[0]):
        xTimer.append(utcToSec(gpsTimeData.m_data["NONE"][i]))

    yTimer = []
    for i in range(esTimeData.m_data.shape[0]):
        yTimer.append(timeTag2ToSec(esTimeData.m_data["NONE"][i]))

    

    # Interpolate
    interpolateLinear(gpsCourseData, xTimer, yTimer, newGPSCourseData)
    interpolateLinear(gpsLatPosData, xTimer, yTimer, newGPSLatPosData)
    interpolateLinear(gpsLonPosData, xTimer, yTimer, newGPSLonPosData)
    interpolateLinear(gpsMagVarData, xTimer, yTimer, newGPSMagVarData)
    interpolateLinear(gpsSpeedData, xTimer, yTimer, newGPSSpeedData)


    newGPSCourseData.columnsToDataset()
    newGPSLatPosData.columnsToDataset()
    newGPSLonPosData.columnsToDataset()
    newGPSMagVarData.columnsToDataset()
    newGPSSpeedData.columnsToDataset()


    #x = darkTimer.m_data["NONE"]
    #y = darkData.m_data[k]
    #new_x = lightTimer.m_data["NONE"]
    #new_y = sp.interpolate.interp1d(x, y, kind='linear', bounds_error=False)(new_x)


# interpolate LT to match LI using spline interpolation
def interpolateSASData(node, liGroup, ltGroup):
    print("Interpolate SAS Data2")

    # LI
    liData = liGroup.getDataset("LI")
    liDateData = liGroup.getDataset("DATETAG")
    liTimeData = liGroup.getDataset("TIMETAG2")

    sasGroup = node.getGroup("SAS")
    newLIData = sasGroup.addDataset("LI_hyperspectral")
    newLTData = sasGroup.addDataset("LT_hyperspectral")


    newLIData.m_columns["Datetag"] = liDateData.m_data["NONE"].tolist()
    newLIData.m_columns["Timetag2"] = liTimeData.m_data["NONE"].tolist()
    for k in liData.m_data.dtype.fields.keys():
        #print("type",type(esData.m_data[k]))
        newLIData.m_columns[k] = liData.m_data[k].tolist()
    newLIData.columnsToDataset()


    # LT
    ltTimeData = ltGroup.getDataset("TIMETAG2")
    ltData = ltGroup.getDataset("LT")

    newLTData.m_columns["Datetag"] = liDateData.m_data["NONE"].tolist()
    newLTData.m_columns["Timetag2"] = liTimeData.m_data["NONE"].tolist()


    xTimer = []
    for i in range(ltTimeData.m_data.shape[0]):
        xTimer.append(timeTag2ToSec(ltTimeData.m_data["NONE"][i]))

    yTimer = []
    for i in range(liTimeData.m_data.shape[0]):
        yTimer.append(timeTag2ToSec(liTimeData.m_data["NONE"][i]))


    # interpolate
    interpolateSpline(ltData, xTimer, yTimer, newLTData)

    newLTData.columnsToDataset()



def processL2s2(root, node):
    esGroup = None
    gpsGroup = None
    liGroup = None
    ltGroup = None
    for gp in root.m_groups:
        if gp.m_id.startswith("GPS"):
            print("GPS")
            gpsGroup = gp
        elif gp.hasDataset("ES") and gp.m_frameType == "ShutterLight":
            print("ES")
            esGroup = gp
        elif gp.hasDataset("LI") and gp.m_frameType == "ShutterLight":
            print("LI")
            liGroup = gp
        elif gp.hasDataset("LT") and gp.m_frameType == "ShutterLight":
            print("LT")
            ltGroup = gp

    interpolateGPSData(node, esGroup, gpsGroup)
    interpolateSASData(node, liGroup, ltGroup)

def processL2s(root):

    processGPSTime(root)

    root2s = HDFRoot()
    root2s.copyAttributes(root)

    root2s.addGroup("GPS")
    root2s.addGroup("Reference")
    root2s.addGroup("SAS")
    #root.processL2s(root2s)
    processL2s2(root, root2s)
    
    return root2s



def main():

    calibrationMap = readCalibrationFile("cal2013.sip")
    print("calibrationMap:", list(calibrationMap.keys()))
    root = readRawFile("data.raw", calibrationMap)
    generateContext(root)
    #print("HDFFile:")
    #root.prnt()
    writeHDFFile("data_L1a.hdf", root)
    root = readHDFFile("data_L1a.hdf")
    generateContext(root)
    #print("HDFFile:")
    #root.prnt()


    print("ProcessL1a:")
    root.processL1a(calibrationMap)
    writeHDFFile("data_L1b.hdf", root)

    print("ProcessL2:")
    root = readHDFFile("data_L1b.hdf")
    generateContext(root)
    #print("Start Time:", root.getStartTime())

    root.processTIMER()

    #for key in calibrationMap:
    #    print(key)

    root.processL2()
    writeHDFFile("data_L2.hdf", root)
    root = readHDFFile("data_L2.hdf")
    generateContext(root)

    root = processL2s(root)
    #root.prnt()
    writeHDFFile("data_L2s.hdf", root)
    root = readHDFFile("data_L2s.hdf")
    generateContext(root)


if __name__ == "__main__":
    main()
