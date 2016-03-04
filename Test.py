
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
            if os.path.splitext(finfo.filename)[1] == ".cal" or \
               os.path.splitext(finfo.filename)[1] == ".tdf":
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

    context = []
    context.append((b"HSL386A.cal", b"SAS", b"Air", b"Surface", b"ShutterLight", b"SATHSL0386"))
    context.append((b"HSL385A.cal", b"SAS", b"Air", b"Surface", b"ShutterLight", b"SATHSL0385"))
    context.append((b"HED488A.cal", b"Reference", b"Air", b"Surface", b"ShutterDark", b"SATHED0488"))
    context.append((b"GPRMC_NoMode.tdf", b"GPS", b"None", b"None", b"None", b"$GPRMC"))
    contextMap = {}
    contextMap["SATHSL0386"] = HDFGroup()
    contextMap["SATHSL0385"] = HDFGroup()
    contextMap["SATHED0488"] = HDFGroup()
    contextMap["$GPRMC"] = HDFGroup()
    contextMap["SATHSL0386"]._id = "SAS"
    contextMap["SATHSL0385"]._id = "SAS2"
    contextMap["SATHED0488"]._id = "Reference"
    contextMap["$GPRMC"]._id = "GPS"

    root = HDFGroup()
    root._id = "/"
    #root._attributes.append((b"PROSOFT", "Prosoft"));
    #root._attributes.append((b"PROSOFT_INSTRUMENT_CONFIG", "Prosoft"));
    #root._attributes.append((b"PROSOFT_PARAMETERS_FILE_NAME", "Prosoft"));
    #root._attributes.append((b"CAL_FILE_NAMES", "Prosoft"));
    #root._attributes.append((b"WAVELENGTH_UNITS", "nm"));
    #root._attributes.append((b"LU_UNITS", "count"));
    #root._attributes.append((b"ED_UNITS", "count"));
    #root._attributes.append((b"ES_UNITS", "count"));
    root._attributes.append((b"RAW_FILE_NAME", "data.RAW"));
    
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
                    print("SATHDR")
                    if i > 0:
                        fp.read(i)
                    b = fp.read(128)
                    (k,v) = readSATHDR(b)
                    root._attributes.append((k,v));
                    
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

                            #cf = calibrationMap[key.lower()]
                            cf = calibrationMap[key]
                            num = cf.convertRaw(b, gp)
                            fp.read(num)

                            i = 32
                            break
                    if i == 32:
                        break

    root._attributes.append(("PROCESSING_LEVEL", "1a"));
    dt = datetime.now()
    dtstr = dt.strftime("%d-%b-%Y %H:%M:%S")
    root._attributes.append(("FILE_CREATION_TIME", dtstr));

    root._groups.append(contextMap["SATHSL0386"])
    root._groups.append(contextMap["SATHSL0385"])
    root._groups.append(contextMap["SATHED0488"])
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
    
    

def main():
    calibrationMap = readCalibrationFile("SolarTracker_2.sip")
    print("calibrationMap:", list(calibrationMap.keys()))
    root = readRawFile("data.RAW", calibrationMap)
    #print("HDFFile:")
    #root.prnt()
    writeHDFFile("data.hdf", root)
    root = readHDFFile("data.hdf")
    print("HDFFile:")
    root.prnt()

if __name__ == "__main__":
    main()
