
import binascii
import math
import struct
import sys

class CalibrationData:
    def __init__(self):
        self.m_type = ""
        self.m_id = ""
        self.m_units = ""
        self.m_fieldLength = 0
        self.m_dataType = ""
        self.m_calLines = 0
        self.m_fitType = ""
        self.m_coefficients = []

    def prnt(self):
        print("%s %s \'%s\' %d %s %d %s" % (self.m_type, self.m_id, self.m_units,
                                     self.m_fieldLength, self.m_dataType,
                                     self.m_calLines, self.m_fitType))
        print("coefficients = ", self.m_coefficients)

    # Reads a sensor definition line from a cal file
    # Reference: (SAT-DN-00134_Instrument File Format.pdf)
    def read(self, line):
        parts = line.split()
        self.m_type = parts[0]
        self.m_id = parts[1]
        self.m_units = parts[2][1:-1]
        self.m_fieldLength = -1 if parts[3].upper() == 'V' else int(parts[3])
        self.m_dataType = parts[4]
        self.m_calLines = int(parts[5])
        self.m_fitType = parts[6]

    # Reads a coefficients line in the cal file
    # Notes: Does not support for OPTIC1, which uses 1-4 calibration lines
    def readCoefficients(self, line):
        self.m_coefficients = line.split()


    # Duplicates functionality of Python 3, int.from_bytes() for use in Python 2
    def intFromBytes(self, data, byteorder='big', signed=False):
        #print("Data",data)
        if byteorder == 'little':
            data = reversed(data)
        val = int(binascii.hexlify(data), 16)
        if signed:
            bits = 4 * (len(val) - 1)
            if val >= math.pow(2, bits-1):
                val = int(0 - (math.pow(2, bits) - val))
        return val

    # Function used when reading a raw file to convert binary data to correct type
    def convertRaw(self, b):
        v = 0
        dataType = self.m_dataType.upper()
        if dataType == "BU":
            if sys.version_info[0] < 3:
                v = self.intFromBytes(b, 'big', False)
            else:
                v = int.from_bytes(b, byteorder='big', signed=False)
            #print("bu", v)
        elif dataType == "BULE":
            if sys.version_info[0] < 3:
                v = self.intFromBytes(b, 'little', False)
            else:
                v = int.from_bytes(b, byteorder='little', signed=False)
            #print("bule", v)
        elif dataType == "BS":
            if sys.version_info[0] < 3:
                v = self.intFromBytes(b, 'big', True)
            else:
                v = int.from_bytes(b, byteorder='big', signed=True)
            #print("bs", v)
        elif dataType == "BSLE":
            if sys.version_info[0] < 3:
                v = self.intFromBytes(b, 'little', True)
            else:
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
            if self.m_type.upper() == "NMEA_CHECKSUM":
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

