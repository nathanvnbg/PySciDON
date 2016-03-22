
import numpy as np

from CalibrationData import CalibrationData
#from HDFGroup import HDFGroup
#from HDFDataset import HDFDataset


class CalibrationFile:
    def __init__(self):
        self.m_id = ""
        self.m_name = ""
        self.m_data = []

    def prnt(self):
        if len(self.m_id) != 0:
            print("id:", self.m_id)
        for cd in self.m_data:
            cd.prnt()

    def read(self, f):
        self.m_name = f.name
        while 1:
            line = f.readline().decode("utf-8")
            #print(line)
            if not line:
                break
            line = line.strip()
            if line.startswith("#") or len(line) == 0:
                continue

            cd = CalibrationData()
            cd.read(line)

            cdtype = cd.m_type.upper()

            if cdtype == "INSTRUMENT" or cdtype == "VLF_INSTRUMENT" or \
               cdtype == "SN" or cdtype == "VLF_SN":
                self.m_id += cd.m_id

            for i in range(0, cd.m_calLines):
                line = f.readline()
                cd.readCoefficients(line)

            #cd.prnt()
            self.m_data.append(cd)


    def convertRaw(self, f, gp):
        nRead = 0

        #for i in range(0, len(self.m_data)):
        #    self.m_data[i].prnt()
        #print("file:", f)

        for i in range(0, len(self.m_data)):
            v = 0
            cd = self.m_data[i]

            if cd.m_fieldLength == -1:
                delimiter = self.m_data[i+1].m_units
                #delimiter = delimiter.decode('string_escape')
                #delimiter = bytes(delimiter, "utf-8").decode("unicode_escape")
                #delimiter = bytes(delimiter.decode("unicode_escape"), "utf-8")
                delimiter = delimiter.encode("utf-8").decode("unicode_escape").encode("utf-8")
                #print("delimiter:", delimiter)

                end = f[nRead:].find(delimiter)
                #print("read:", nRead, end)
                b = f[nRead:nRead+end]
                v = cd.convertRaw(b)

                nRead += end

            else:
                if cd.m_fitType.upper() != "DELIMITER":
                    if cd.m_fieldLength != 0:
                        b = f[nRead:nRead+cd.m_fieldLength]
                        #print(nRead, cd.m_fieldLength, b)
                        v = cd.convertRaw(b)
                nRead  += cd.m_fieldLength

            if cd.m_fitType.upper() != "NONE" and cd.m_fitType.upper() != "DELIMITER":
                cdtype = cd.m_type.upper()
                if cdtype != "INSTRUMENT" and cdtype != "VLF_INSTRUMENT" and \
                   cdtype != "SN" and cdtype != "VLF_SN":
                    ds = gp.getDataset(cd.m_type)
                    #print(cd.m_id)
                    #ds.m_temp.append(v)
                    #ds.addColumn(cd.m_id)
                    ds.appendColumn(cd.m_id, v)


            #print("Key:", key)
            # optimize later y storing as list then batch convert with np.asarray()
        #    if ds.m_data is not None:
        #        ds.m_data = np.vstack((ds.m_data, np.asarray(ds.m_temp)))
        #    else:
        #        ds.m_data = np.asarray(ds.m_temp)
        #    ds.m_temp = []

        # Satview records additional bytes
        # 3 bytes date tag, 4 bytes time tag
        if not gp.m_id.startswith("GPS"):
            #print("not gps")
            # date tag
            b = f[nRead:nRead+3]
            v = int.from_bytes(b, byteorder='big', signed=False)
            nRead += 3
            #print("Date:",v)
            ds1 = gp.getDataset("DATETAG")
            ds1.appendColumn("NONE", v)

            b = f[nRead:nRead+4]
            v = int.from_bytes(b, byteorder='big', signed=False)
            nRead += 4
            #print("Time:",v)
            ds1 = gp.getDataset("TIMETAG2")
            ds1.appendColumn("NONE", v)


        return nRead

