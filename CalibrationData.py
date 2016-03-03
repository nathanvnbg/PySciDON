
import struct

class CalibrationData:
    def __init__(self):
        self._type = b""
        self._id = b""
        self._units = b""
        self._fieldLength = 0
        self._dataType = b""
        self._calLines = 0
        self._fitType = b""
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
        self._fieldLength = -1 if parts[3].lower() == b'v' else int(parts[3])
        self._dataType = parts[4]
        self._calLines = int(parts[5])
        self._fitType = parts[6]

    def readCoefficients(self, line):
        self._coefficients = line.split()
        
    def convertRaw(self, b):
        v = 0
        dataType = self._dataType.lower()
        if dataType == b"bu":
            v = int.from_bytes(b, byteorder='big', signed=False)
            #print("bu", v)
        elif dataType == b"bule":
            v = int.from_bytes(b, byteorder='little', signed=False)
            #print("bule", v)
        elif dataType == b"bs":
            v = int.from_bytes(b, byteorder='big', signed=True)
            #print("bs", v)
        elif dataType == b"bsle":
            v = int.from_bytes(b, byteorder='little', signed=True)
            #print("bsle", v)
        elif dataType == b"bf":
            v = struct.unpack("f", b)[0]
            #print("bf", v)
        elif dataType == b"bd":
            v = struct.unpack("d", b)[0]
            #print("bd", v)
        elif dataType == b"hs":
            v = int(b.encode('hex'), 16)
            #print("hs", v)
        elif dataType == b"hu":
            v = int(b.encode('hex'), 16)
            #print("hu", v)
        elif dataType == b"ai":
            v = int(b)
            #print("ai", v)
        elif dataType == b"au":
            v = int(b)
            #print("au", v)
        elif dataType == b"af":
            v = float(b)
            #print("af", v)
        elif dataType == b"as":
            v = b
            #print("as", v)
        else:
            v = -1
            print("dataType unknown: ", dataType)
        return v

