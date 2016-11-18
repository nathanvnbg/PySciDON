
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
#        for cd in self.m_data:
#            cd.printd()

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

            # Determines the frame synchronization string by appending
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

    # Returns the sensor type
    def getSensorType(self):
        for cd in self.m_data:
            if cd.m_type == "ES" or \
               cd.m_type == "LI" or \
               cd.m_type == "LT":
                return cd.m_type
        return "None"

    # Verify raw data message can be read successfully
    def verifyRaw(self, msg):
        try:
            nRead = 0
            for i in range(0, len(self.m_data)):
                v = 0
                cd = self.m_data[i]

                # Read variable length message frames (field length == -1)
                if cd.m_fieldLength == -1:
                    delimiter = self.m_data[i+1].m_units
                    delimiter = delimiter.encode("utf-8").decode("unicode_escape").encode("utf-8")
                    #print("delimiter:", delimiter)

                    end = msg[nRead:].find(delimiter)
                    #print("read:", nRead, end)
                    if end == 0:
                        v = 0.0
                    else:
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
                
                # Passed EndOfFile
                #if nRead > len(msg):
                #    return False

            return True

        except:
            pass
            #print("Failed to read message successfully")

        return False


    # Reads a message frame from the raw file and generates hdf groups/datasets
    # Returns nRead (number of bytes read) or -1 on error
    def convertRaw(self, msg, gp):
        nRead = 0
        instrumentId = ""

        #for i in range(0, len(self.m_data)):
        #    self.m_data[i].printd()
        #print("file:", msg)

        if self.verifyRaw(msg) == False:
            #print("Message not read successfully:\n" + str(msg))
            return -1

        for i in range(0, len(self.m_data)):
            v = 0
            cd = self.m_data[i]


            # Get value from message frame

            # Read variable length message frames (field length == -1)
            if cd.m_fieldLength == -1:
                delimiter = self.m_data[i+1].m_units
                delimiter = delimiter.encode("utf-8").decode("unicode_escape").encode("utf-8")
                #print("delimiter:", delimiter)

                end = msg[nRead:].find(delimiter)
                if end == 0:
                    v = 0.0
                else:
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


            # Stores the instrument id to check for DATETAG/TIMETAG2
            if cd.m_type.upper() == "INSTRUMENT" or cd.m_type.upper() == "VLF_INSTRUMENT":
                instrumentId = cd.m_id


            # Stores value in dataset or attribute depending on type

            # Stores raw data into hdf datasets according to type
            if cd.m_fitType.upper() != "NONE" and cd.m_fitType.upper() != "DELIMITER":
                cdtype = cd.m_type.upper()
                if cdtype != "INSTRUMENT" and cdtype != "VLF_INSTRUMENT" and \
                   cdtype != "SN" and cdtype != "VLF_SN":
                    ds = gp.getDataset(cd.m_type)
                    if ds is None:
                        ds = gp.addDataset(cd.m_type)
                    #print(cd.m_id)
                    #ds.m_temp.append(v)
                    #ds.addColumn(cd.m_id)
                    ds.appendColumn(cd.m_id, v)
                else:
                    # ToDo: move to better position
                    if sys.version_info[0] < 3: # Python3
                        gp.m_attributes[cdtype.encode('utf-8')] = cd.m_id
                    else: # Python2
                        gp.m_attributes[cdtype] = cd.m_id

            # None types are stored as attributes
            if cd.m_fitType.upper() == "NONE":
                cdtype = cd.m_type.upper()
                if cdtype == "SN" or cdtype == "DATARATE" or cdtype == "RATE":
                    # ToDo: move to better position
                    if sys.version_info[0] < 3:
                        gp.m_attributes[cdtype.encode('utf-8')] = cd.m_id
                    else:
                        gp.m_attributes[cdtype] = cd.m_id


        # Some instruments produce additional bytes for
        # DATETAG (3 bytes), and TIMETAG2 (4 bytes)
        if instrumentId.startswith("SATHED") or \
                instrumentId.startswith("SATHLD") or \
                instrumentId.startswith("SATHSE") or \
                instrumentId.startswith("SATHSL") or \
                instrumentId.startswith("SATPYR") or \
                instrumentId.startswith("SATNAV"):
            #print("not gps")
            # Read DATETAG
            b = msg[nRead:nRead+3]
            if sys.version_info[0] < 3:
                v = int(binascii.hexlify(b), 16)
            else:
                v = int.from_bytes(b, byteorder='big', signed=False)
            nRead += 3
            #print("Date:",v)
            ds1 = gp.getDataset("DATETAG")
            if ds1 is None:
                ds1 = gp.addDataset("DATETAG")
            ds1.appendColumn(u"NONE", v)

            # Read TIMETAG2
            b = msg[nRead:nRead+4]
            if sys.version_info[0] < 3:
                v = int(binascii.hexlify(b), 16)
            else:
                v = int.from_bytes(b, byteorder='big', signed=False)
            nRead += 4
            #print("Time:",v)
            ds1 = gp.getDataset("TIMETAG2")
            if ds1 is None:
                ds1 = gp.addDataset("TIMETAG2")
            ds1.appendColumn(u"NONE", v)

        return nRead

