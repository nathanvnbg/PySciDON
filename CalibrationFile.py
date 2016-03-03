
from CalibrationData import CalibrationData
from HDFGroup import HDFGroup
from HDFDataset import HDFDataset


class CalibrationFile:
    def __init__(self):
        self._id = b""
        self._data = []

    def prnt(self):
        if len(self._id) != 0:
            print("id:", _id)
        for cd in self._data:
            cd.prnt()

    def read(self, f):
        while 1:
            line = f.readline()
            #print(line)
            if not line:
                break
            line = line.strip()
            if line.startswith(b"#") or len(line) == 0:
                continue

            cd = CalibrationData()
            cd.read(line)

            cdtype = cd._type.lower()
            
            if cdtype == b"instrument" or cdtype == b"vlf_instrument" or \
               cdtype == b"sn" or cdtype == b"vlf_sn":
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
                delimiter = bytes(delimiter.decode("unicode_escape"), "utf-8")
                #print("delimiter:", delimiter)

                end = f[nRead:].find(delimiter)
                #print("read:", nRead, end)
                b = f[nRead:nRead+end]
                v = cd.convertRaw(b)

                nRead += end

            else:
                if cd._fitType.lower() != b"delimiter":
                    if cd._fieldLength != 0:
                        b = f[nRead:nRead+cd._fieldLength]
                        #print(nRead, cd._fieldLength, b)
                        v = cd.convertRaw(b)
                nRead  += cd._fieldLength

            if cd._fitType.lower() != b"none" and cd._fitType.lower() != b"delimiter":
                cdtype = cd._type.lower()
                if cdtype != b"instrument" and cdtype != b"vlf_instrument" and \
                   cdtype != b"sn" and cdtype != b"vlf_sn":
                    ds = gp.getDataset(cd._type)
                    ds._data.append(v)

        return nRead

        
