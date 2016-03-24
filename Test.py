
import collections
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
        frameTag = gp.m_attributes["FrameTag"]
        #print(line)
        if frameTag == "SATHED0150":
            #gp.m_id = "Reference"
            #gp.m_sensorType = "ES"
            gp.m_attributes["InstrumentType"] = "Reference"
            gp.m_attributes["Media"] = "Air"
            gp.m_attributes["MeasMode"] = "Surface"
            gp.m_attributes["FrameType"] = "ShutterDark"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.getTableHeader("ES")
            gp.m_attributes["DISTANCE_1"] = "Pressure ES 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface ES 1 1 0"
        elif frameTag == "SATHLD0151":
            #gp.m_id = "SAS"
            #gp.m_sensorType = "LI"
            gp.m_attributes["InstrumentType"] = "SAS"
            gp.m_attributes["Media"] = "Air"
            gp.m_attributes["MeasMode"] = "VesselBorne"
            gp.m_attributes["FrameType"] = "ShutterDark"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.getTableHeader("LI")
            gp.m_attributes["DISTANCE_1"] = "Pressure LI 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface LI 1 1 0"
        elif frameTag == "SATHLD0152":
            #gp.m_id = "SAS"
            #gp.m_sensorType = "LT"
            gp.m_attributes["InstrumentType"] = "SAS"
            gp.m_attributes["Media"] = "Air"
            gp.m_attributes["MeasMode"] = "VesselBorne"
            gp.m_attributes["FrameType"] = "ShutterDark"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.getTableHeader("LT")
            gp.m_attributes["DISTANCE_1"] = "Pressure LT 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface LT 1 1 0"
        elif frameTag == "SATHSE0150":
            #gp.m_id = "Reference"
            #gp.m_sensorType = "ES"
            gp.m_attributes["InstrumentType"] = "Reference"
            gp.m_attributes["Media"] = "Air"
            gp.m_attributes["MeasMode"] = "Surface"
            gp.m_attributes["FrameType"] = "ShutterLight"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.getTableHeader("ES")
            gp.m_attributes["DISTANCE_1"] = "Pressure ES 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface ES 1 1 0"
        elif frameTag == "SATHSL0151":
            #gp.m_id = "SAS"
            #gp.m_sensorType = "LI"
            gp.m_attributes["InstrumentType"] = "SAS"
            gp.m_attributes["Media"] = "Air"
            gp.m_attributes["MeasMode"] = "VesselBorne"
            gp.m_attributes["FrameType"] = "ShutterLight"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.getTableHeader("LI")
            gp.m_attributes["DISTANCE_1"] = "Pressure LI 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface LI 1 1 0"
        elif frameTag == "SATHSL0152":
            #gp.m_id = "SAS"
            #gp.m_sensorType = "LT"
            gp.m_attributes["InstrumentType"] = "SAS"
            gp.m_attributes["Media"] = "Air"
            gp.m_attributes["MeasMode"] = "VesselBorne"
            gp.m_attributes["FrameType"] = "ShutterLight"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.getTableHeader("LT")
            gp.m_attributes["DISTANCE_1"] = "Pressure LT 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface LT 1 1 0"
        elif frameTag == "SATSAS0052":
            #gp.m_id = "SAS"
            #gp.m_sensorType = "None"
            gp.m_attributes["InstrumentType"] = "SAS"
            gp.m_attributes["Media"] = "Air"
            gp.m_attributes["MeasMode"] = "VesselBorne"
            gp.m_attributes["FrameType"] = "LightAncCombined"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.m_attributes["Head_1"] = "ANC 1 1 None"
            gp.m_attributes["DISTANCE_1"] = "Pressure ANC 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface ANC 1 1 0"
            gp.m_attributes["SN"] = "0052"
        elif frameTag == "$GPRMC":
            #gp.m_id = "GPS"
            #gp.m_sensorType = "None"
            gp.m_attributes["InstrumentType"] = "GPS"
            gp.m_attributes["Media"] = "Not Required"
            gp.m_attributes["MeasMode"] = "Not Required"
            gp.m_attributes["FrameType"] = "Not Required"
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.m_attributes["Head_1"] = "GPS 1 1 None"
            gp.m_attributes["DISTANCE_1"] = "Pressure GPS 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface GPS 1 1 0"
            gp.m_attributes["VLF_INSTRUMENT"] = "$GPRMC"




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
    root.m_attributes["PROSOFT"] = "Prosoft 7.7.16_6"
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


def interpolateWavelength(ds, newDS):

    # Copy dataset to dictionary
    columns = collections.OrderedDict()
    for k in [x for x,y in sorted(ds.m_data.dtype.fields.items(),key=lambda k: k[1])]:
        #print("type",type(esData.m_data[k]))
        columns[k] = ds.m_data[k].tolist()
    saveDatetag = columns.pop("Datetag")
    saveTimetag2 = columns.pop("Timetag2")


    # Get wavelength values
    wavelength = []
    for k in columns:
        #print(k)
        wavelength.append(float(k))
    x = np.asarray(wavelength)


    # Determine interpolated wavelength values
    start = np.ceil(wavelength[0])
    end = np.floor(wavelength[len(wavelength)-1])
    new_x = np.arange(start, end, 1)
    #print(new_x)

    newColumns = collections.OrderedDict()
    newColumns["Datetag"] = saveDatetag
    newColumns["Timetag2"] = saveTimetag2
    for i in range(new_x.shape[0]):
        #print(i, new_x[i])
        newColumns[str(new_x[i])] = []

    # Perform interpolation for each row
    for i in range(len(saveDatetag)):
        #print(i)

        values = []
        for k in columns:
            values.append(columns[k][i])
        y = np.asarray(values)
        new_y = interpolate.interp1d(x, y)(new_x)
        
        # Natural log transformation
        #new_y = np.log(new_y)
        
        # Exp transformation
        #new_y = np.exp(new_y)

        for i in range(new_x.shape[0]):
            newColumns[str(new_x[i])].append(new_y[i])


    #newDS = HDFDataset()
    newDS.m_columns = newColumns
    newDS.columnsToDataset()
    #print(ds.m_columns)
    #return newDS

def dataAveraging(ds):
    # Copy dataset to dictionary
    columns = collections.OrderedDict()
    for k in [x for x,y in sorted(ds.m_data.dtype.fields.items(),key=lambda k: k[1])]:
        #print("type",type(esData.m_data[k]))
        columns[k] = ds.m_data[k].tolist()
    saveDatetag = columns.pop("Datetag")
    saveTimetag2 = columns.pop("Timetag2")

    newColumns = collections.OrderedDict()

    # Average data in each column
    for k in [x for x,y in sorted(ds.m_data.dtype.fields.items(),key=lambda k: k[1])]:
        #print(k)
        d = ds.m_data[k]

        # Natural log transformation
        d = np.log(d)        
        
        l = []
        i = 2
        while i < (len(ds.m_data[k]) - 2):
            if k == "Datatag" or k == "Timetag2":
                l.append(d[i])
            else:
                x0 = float(d[i-1])
                x1 = float(d[i])
                x2 = float(d[i+1])
                avg = (x0+x1+x2)/3
                l.append(avg)
            i += 2

        # Exp transformation
        d = np.exp(l)

        newColumns[k] = d


    #newDS = HDFDataset()
    ds.m_columns = newColumns
    ds.columnsToDataset()
    #print(ds.m_columns)
    #print(len(newColumns["Datetag"]))
    #return newDS


def processL3a(root):

    root3a = HDFRoot()
    root3a.copyAttributes(root)
    root3a.m_attributes["PROCESSING_LEVEL"] = "3a"
    root3a.m_attributes["BIN_INTERVAL"] = "1 m"
    root3a.m_attributes["BIN_WIDTH"] = "0.5 m"
    root3a.m_attributes["TIME_INTERVAL"] = "2 sec"
    root3a.m_attributes["TIME_WIDTH"] = "1 sec"
    root3a.m_attributes["WAVEL_INTERP"] = "1 nm"

    referenceGroup3a = root3a.addGroup("Reference")
    sasGroup3a = root3a.addGroup("SAS")
    root3a.m_groups.append(root.getGroup("GPS"))

    referenceGroup = root.getGroup("Reference")
    sasGroup = root.getGroup("SAS")

    esData = referenceGroup.getDataset("ES_hyperspectral")
    liData = sasGroup.getDataset("LI_hyperspectral")
    ltData = sasGroup.getDataset("LT_hyperspectral")

    newESData = referenceGroup3a.addDataset("ES_hyperspectral")
    newLIData = sasGroup3a.addDataset("LI_hyperspectral")
    newLTData = sasGroup3a.addDataset("LT_hyperspectral")

    interpolateWavelength(esData, newESData)
    interpolateWavelength(liData, newLIData)
    interpolateWavelength(ltData, newLTData)
    
    dataAveraging(newESData)
    dataAveraging(newLIData)
    dataAveraging(newLTData)

    return root3a


def main():

    calibrationMap = readCalibrationFile("cal2013.sip")
    print("calibrationMap:", list(calibrationMap.keys()))
    root = readRawFile("data.raw", calibrationMap)
    generateContext(root)
    #print("HDFFile:")
    #root.prnt()
    writeHDFFile("data_L1a.hdf", root)
    root = readHDFFile("data_L1a.hdf")
    #print("HDFFile:")
    #root.prnt()
    
    #gp.m_attributes["Head_1"] = "ES 1 1 355.36"
    #gp.m_attributes["Head_2"] = "ES 1 1 358.66"
    #gp.m_attributes["Head_3"] = "ES 1 1 361.95"
    #gp.m_attributes["Head_4"] = "ES 1 1 365.25"
    #gp.m_attributes["Head_5"] = "ES 1 1 368.54"


    print("ProcessL1a:")
    root.processL1b(calibrationMap)
    writeHDFFile("data_L1b.hdf", root)


    print("ProcessL2:")
    root = readHDFFile("data_L1b.hdf")
    #print("Start Time:", root.getStartTime())

    root.processTIMER()

    #for key in calibrationMap:
    #    print(key)

    root.processL2()
    writeHDFFile("data_L2.hdf", root)
    root = readHDFFile("data_L2.hdf")


    print("ProcessL2s:")
    processGPSTime(root)
    root = root.processL2s()
    #root.prnt()
    writeHDFFile("data_L2s.hdf", root)
    root = readHDFFile("data_L2s.hdf")
    
    print("ProcessL3a:")
    root = processL3a(root)
    writeHDFFile("data_L3a.hdf", root)
    root = readHDFFile("data_L3a.hdf")


if __name__ == "__main__":
    main()
