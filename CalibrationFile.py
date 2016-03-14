
import numpy as np

from CalibrationData import CalibrationData
#from HDFGroup import HDFGroup
#from HDFDataset import HDFDataset


class CalibrationFile:
    def __init__(self):
        self._id = ""
        self._name = ""
        self._data = []

    def prnt(self):
        if len(self._id) != 0:
            print("id:", self._id)
        for cd in self._data:
            cd.prnt()

    def read(self, f):
        self._name = f.name
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

            cdtype = cd._type.upper()
            
            if cdtype == "INSTRUMENT" or cdtype == "VLF_INSTRUMENT" or \
               cdtype == "SN" or cdtype == "VLF_SN":
                self._id += cd._id

            for i in range(0, cd._calLines):
                line = f.readline()
                cd.readCoefficients(line)

            #cd.prnt()
            self._data.append(cd)


    def convertRaw(self, f, gp):
        nRead = 0

        #for i in range(0, len(self._data)):
        #    self._data[i].prnt()
        #print("file:", f)

        for i in range(0, len(self._data)):
            v = 0
            cd = self._data[i]

            if cd._fieldLength == -1:
                delimiter = self._data[i+1]._units
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
                if cd._fitType.upper() != "DELIMITER":
                    if cd._fieldLength != 0:
                        b = f[nRead:nRead+cd._fieldLength]
                        #print(nRead, cd._fieldLength, b)
                        v = cd.convertRaw(b)
                nRead  += cd._fieldLength

            if cd._fitType.upper() != "NONE" and cd._fitType.upper() != "DELIMITER":
                cdtype = cd._type.upper()
                if cdtype != "INSTRUMENT" and cdtype != "VLF_INSTRUMENT" and \
                   cdtype != "SN" and cdtype != "VLF_SN":
                    ds = gp.getDataset(cd._type)
                    ds._temp.append(v)
                    ds.addColumn(cd._id)

        
        for ds in gp._datasets:
            # optimize later y storing as list then batch convert with np.asarray()
            if ds._data != None:
                ds._data = np.vstack((ds._data, ds._temp))
            else:
                ds._data = np.asarray(ds._temp)
            ds._temp = []


        return nRead

        
