
import struct

class CalibrationData:
    def __init__(self):
        self._type = ""
        self._id = ""
        self._units = ""
        self._fieldLength = 0
        self._dataType = ""
        self._calLines = 0
        self._fitType = ""
        self._coefficients = []

    def prnt(self):
        print("%s %s \'%s\' %d %s %d %s" % (self._type, self._id, self._units,
                                     self._fieldLength, self._dataType,
                                     self._calLines, self._fitType))
        print("coefficients = ", self._coefficients)

    def read(self, line):
        parts = line.split()
        self._type = parts[0]
        self._id = parts[1]
        self._units = parts[2][1:-1]
        self._fieldLength = -1 if parts[3].upper() == 'V' else int(parts[3])
        self._dataType = parts[4]
        self._calLines = int(parts[5])
        self._fitType = parts[6]

    def readCoefficients(self, line):
        self._coefficients = line.split()
        
    def convertRaw(self, b):
        v = 0
        dataType = self._dataType.upper()
        if dataType == "BU":
            v = int.from_bytes(b, byteorder='big', signed=False)
            #print("bu", v)
        elif dataType == "BULE":
            v = int.from_bytes(b, byteorder='little', signed=False)
            #print("bule", v)
        elif dataType == "BS":
            v = int.from_bytes(b, byteorder='big', signed=True)
            #print("bs", v)
        elif dataType == "BSLE":
            v = int.from_bytes(b, byteorder='little', signed=True)
            #print("bsle", v)
        elif dataType == "BF":
            v = struct.unpack("f", b)[0]
            #print("bf", v)
        elif dataType == "BD":
            v = struct.unpack("d", b)[0]
            #print("bd", v)
        elif dataType == "HS":
            v = int(b, 16)
            #print("hs", v)
        elif dataType == "HU":
            v = int(b, 16)
            #print("hu", v)
        elif dataType == "AI":
            if self._type.upper() == "NMEA_CHECKSUM":
                v = int(b, 16)
            else:
                v = int(b)
            #print("ai", v)
        elif dataType == "AU":
            v = int(b)
            #print("au", v)
        elif dataType == "AF":
            v = float(b)
            #print("af", v)
        elif dataType == "AS":
            #v = b.decode("utf-8")
            v = b
            #print("as", v)
        else:
            v = -1
            print("dataType unknown: ", dataType)
        return v

