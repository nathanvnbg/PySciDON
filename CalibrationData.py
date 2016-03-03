
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
        dataType = self._dataType.lower()
        if dataType == b"bu":
            print("bu", int.from_bytes(b, byteorder='big', signed=False))
        elif dataType == b"bule":
            print("bule", int.from_bytes(b, byteorder='little', signed=False))
        elif dataType == b"bs":
            print("bs", int.from_bytes(b, byteorder='big', signed=True))
        elif dataType == b"bsle":
            print("bsle", int.from_bytes(b, byteorder='little', signed=True))
        elif dataType == b"bf":
            print("bf", struct.unpack("f", b)[0])
        elif dataType == b"bd":
            print("bd", struct.unpack("d", b)[0])
        elif dataType == b"hs":
            print("hs", int(b.encode('hex'), 16))
        elif dataType == b"hu":
            print("hu", int(b.encode('hex'), 16))
        elif dataType == b"ai":
            print("ai", int(b))
        elif dataType == b"au":
            print("au", int(b))
        elif dataType == b"af":
            print("af", float(b))
        elif dataType == b"as":
            print("as", b)
        else:
            print("dataType unknown: ", dataType)
            
            
