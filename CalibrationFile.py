
import binascii
import os
import sys

from CalibrationData import CalibrationData
#from HDFGroup import HDFGroup
#from HDFDataset import HDFDataset


# CalibrationFile class stores information about an instrument
# obtained from reading a calibration file
class CalibrationFile:
    def __init__(self):
        self.m_id = ""
        self.m_name = ""
        self.m_data = []
        
        self.m_instrumentType = ""
        self.m_media = ""
        self.m_measMode = ""
        self.m_frameType = ""
        self.m_sensorType = ""


    def printd(self):
        if len(self.m_id) != 0:
            print("id:", self.m_id)
        for cd in self.m_data:
            cd.printd()

    # Reads a calibration file and generates calibration data
    def read(self, f):
        (dirpath, filename) = os.path.split(f.name)
        self.m_name = filename
        while 1:
            line = f.readline()
            line = line.decode("utf-8")
            #print(line)
            if not line:
                break
            line = line.strip()
            
            # Ignore comments and empty lines
            if line.startswith("#") or len(line) == 0:
                continue

            cd = CalibrationData()
            cd.read(line)

            cdtype = cd.m_type.upper()

            # Determines the frame syncronization string by appending
            # ids from INSTRUMENT and SN lines
            # ToDo: Add a check to ensure INSTRUMENT and SN are the first two lines
            if cdtype == "INSTRUMENT" or cdtype == "VLF_INSTRUMENT" or \
               cdtype == "SN" or cdtype == "VLF_SN":
                self.m_id += cd.m_id

            # Read in coefficients
            for i in range(0, cd.m_calLines):
                line = f.readline()
                cd.readCoefficients(line)

            #cd.printd()
            self.m_data.append(cd)

    # Returns units for the calibration data with type t
    def getUnits(self, t):
        for cd in self.m_data:
            if cd.m_type == t:
                return cd.m_units
        return None


    # Reads a message frame from the raw file and generates hdf groups/datasets
    def convertRaw(self, msg, gp):
        nRead = 0

        #for i in range(0, len(self.m_data)):
        #    self.m_data[i].printd()
        #print("file:", msg)

        for i in range(0, len(self.m_data)):
            v = 0
            cd = self.m_data[i]

            # Read variable length message frames, field length == -1
            if cd.m_fieldLength == -1:
                delimiter = self.m_data[i+1].m_units
                delimiter = delimiter.encode("utf-8").decode("unicode_escape").encode("utf-8")
                #print("delimiter:", delimiter)

                end = msg[nRead:].find(delimiter)
                #print("read:", nRead, end)
                b = msg[nRead:nRead+end]
                v = cd.convertRaw(b)

                nRead += end

            # Read fixed length message frames
            else:
                if cd.m_fitType.upper() != "DELIMITER":
                    if cd.m_fieldLength != 0:
                        b = msg[nRead:nRead+cd.m_fieldLength]
                        #print(nRead, cd.m_fieldLength, b)
                        v = cd.convertRaw(b)
                nRead  += cd.m_fieldLength

            # Stores raw data into hdf datasets according to type
            if cd.m_fitType.upper() != "NONE" and cd.m_fitType.upper() != "DELIMITER":
                cdtype = cd.m_type.upper()
                if cdtype != "INSTRUMENT" and cdtype != "VLF_INSTRUMENT" and \
                   cdtype != "SN" and cdtype != "VLF_SN":
                    ds = gp.getDataset(cd.m_type)
                    #print(cd.m_id)
                    #ds.m_temp.append(v)
                    #ds.addColumn(cd.m_id)
                    ds.appendColumn(cd.m_id, v)
                else:
                    # ToDo: move to better position
                    if sys.version_info[0] < 3:
                        gp.m_attributes[cdtype.encode('utf-8')] = cd.m_id
                    else:
                        gp.m_attributes[cdtype] = cd.m_id

            # None types to store as attributes
            if cd.m_fitType.upper() == "NONE":
                cdtype = cd.m_type.upper()
                if cdtype == "SN" or cdtype == "DATARATE" or cdtype == "RATE":
                    # ToDo: move to better position
                    if sys.version_info[0] < 3:
                        gp.m_attributes[cdtype.encode('utf-8')] = cd.m_id
                    else:
                        gp.m_attributes[cdtype] = cd.m_id 


        # Satview appends additional bytes for DATETAG, TIMETAG2
        # 3 bytes date tag, 4 bytes time tag
        #if not gp.m_id.startswith("GPS"):
        if not gp.hasDataset("UTCPOS"):
            #print("not gps")
            # date tag
            b = msg[nRead:nRead+3]
            if sys.version_info[0] < 3:
                v = int(binascii.hexlify(b), 16)
            else:
                v = int.from_bytes(b, byteorder='big', signed=False)
            nRead += 3
            #print("Date:",v)
            ds1 = gp.getDataset("DATETAG")
            ds1.appendColumn(u"NONE", v)

            b = msg[nRead:nRead+4]
            if sys.version_info[0] < 3:
                v = int(binascii.hexlify(b), 16)
            else:
                v = int.from_bytes(b, byteorder='big', signed=False)
            nRead += 4
            #print("Time:",v)
            ds1 = gp.getDataset("TIMETAG2")
            ds1.appendColumn(u"NONE", v)

        return nRead

