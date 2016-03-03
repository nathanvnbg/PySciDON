
import os.path
import zipfile


from CalibrationData import CalibrationData
from CalibrationFile import CalibrationFile

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


def readRawFile(filepath, calibrationMap):
    with open(filepath, 'rb') as fp:
        while 1:
            pos = fp.tell()
            b = fp.read(32)
            fp.seek(pos)

            if not b:
                break

            #print b
            for i in range(0, 32):
                testString = b[i:].lower()
                #print("test: ", testString[:6])
            
                if i == 31:
                    fp.read(32)
                    break

                if testString.startswith(b"sathdr"):
                    print("sathdr")
                    if i > 0:
                        fp.read(i)
                    fp.read(128)
                    break
                else:
                    for key in calibrationMap:
                        if testString.startswith(key.lower()):
                            if i > 0:
                                fp.read(i)

                            pos = fp.tell()
                            b = fp.read(1024)
                            fp.seek(pos)

                            cf = calibrationMap[key]
                            num = cf.convertRaw(b)
                            fp.read(num)

                            i = 32
                            break
                    if i == 32:
                        break
                
    

def main():
    calibrationMap = readCalibrationFile("SolarTracker_2.sip")
    print("calibrationMap:", list(calibrationMap.keys()))
    readRawFile("data.RAW", calibrationMap)

if __name__ == "__main__":
    main()
