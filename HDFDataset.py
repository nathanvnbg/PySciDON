
import collections

from datetime import datetime

import h5py
import numpy as np

class HDFDataset:
    def __init__(self):
        self.m_id = ""
        self.m_attributes = collections.OrderedDict()
        self.m_columns = collections.OrderedDict()
        self.m_data = None


    def prnt(self):
        print("Dataset:", self.m_id)
        for k in self.m_attributes:
            print(k, self.m_attributes[k])
        #for x in np.nditer(self.m_data, flags=['external_loop'], op_flags=['readwrite']):
        #    x[...] *= 2
            #print(x)
        #print(self.m_data)
        #for d in self.m_data:
        #    d.prnt()

    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        self.m_id = name
        #print("Dataset:", name)

        self.m_data = np.array(f)
        #print("Data:", self.m_data.dtype)


    def write(self, f):
        #print("id:", self.m_id)        
        #print("columns:", self.m_columns)
        #print("data:", self.m_data)

        # h4toh5 converter saves datatypes separately, but this doesn't seem required
        #typeId = self.m_id + "_t"
        #f[typeId] = self.m_data.dtype
        #dset = f.create_dataset(self.m_id, data=self.m_data, dtype=f[typeId])
        if self.m_data is not None:
            dset = f.create_dataset(self.m_id, data=self.m_data, dtype=self.m_data.dtype)
        else:
            print("Dataset.write(): Data is None")



    def getColumn(self, name):
        return self.m_columns[name]

    def appendColumn(self, name, val):
        if name not in self.m_columns:
            self.m_columns[name] = [val]
        else:
            self.m_columns[name].append(val)


    def columnsToDataset(self):
        #print(ds.m_columns)
        #dtype0 = np.dtype([(name, type(ds.m_columns[name][0])) for name in ds.m_columns.keys()])
        dtype = []
        for name in self.m_columns.keys():
            item = self.m_columns[name][0]
            if isinstance(item, bytes):
                #dtype.append((name, h5py.special_dtype(vlen=str)))
                dtype.append((name, "|S" + str(len(item))))
            elif isinstance(item, int): # hdf4 only supports 32 bit int
                dtype.append((name, np.float64))
            else:
                dtype.append((name, type(item)))

        #shape = (len(list(ds.m_columns.values())[0]), len(ds.m_columns))
        shape = (len(list(self.m_columns.values())[0]), )
        #print("Id:", ds.m_id)
        #print("Dtype:", dtype)
        #print("Shape:", shape)
        self.m_data = np.empty(shape, dtype=dtype)
        for k,v in self.m_columns.items():
            self.m_data[k] = v
            #for i in range(len(v)):
            #    ds.m_data[k][i] = v[i]
        #if ds.m_id == "LATHEMI":
        #    print("Data", ds.m_data)


    def processL1a(self, cd, inttime = None):
        #print("FitType:", cd.m_fitType)
        if cd.m_fitType == "OPTIC1":
            self.processOPTIC1(cd, False)
        elif cd.m_fitType == "OPTIC2":
            self.processOPTIC2(cd, False)
        elif cd.m_fitType == "OPTIC3":
            self.processOPTIC3(cd, False, inttime)
        elif cd.m_fitType == "OPTIC4":
            self.processOPTIC4(cd, False)
        elif cd.m_fitType == "THERM1":
            self.processTHERM1(cd)
        elif cd.m_fitType == "POW10":
            self.processPOW10(cd)
        elif cd.m_fitType == "POLYU":
            self.processPOLYU(cd)
        elif cd.m_fitType == "POLYF":
            self.processPOLYF(cd)
        elif cd.m_fitType == "DDMM":
            self.processDDMM(cd)
        elif cd.m_fitType == "HHMMSS":
            self.processHHMMSS(cd)
        elif cd.m_fitType == "DDMMYY":
            self.processDDMMYY(cd)
        elif cd.m_fitType == "TIME2":
            self.processTIME2(cd)
        elif cd.m_fitType == "COUNT":
            pass
        elif cd.m_fitType == "NONE":
            pass
        else:
            print("Unknown Fit Type:", cd.m_fitType)

    def processOPTIC1(self, cd):
        return

    def processOPTIC2(self, cd, immersed):
        #self.m_data = self.m_data.astype(float)
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        k = cd.m_id
        for x in range(self.m_data.shape[0]):
            self.m_data[k][x] = im * a1 * (self.m_data[k][x] - a0)

    def processOPTIC3(self, cd, immersed, inttime):
        #self.m_data = self.m_data.astype(float)
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        cint = float(cd.m_coefficients[3])
        #print(inttime.m_data.shape[0], self.m_data.shape[0])
        k = cd.m_id
        #print(cint, aint)
        #print(cd.m_id)
        for x in range(self.m_data.shape[0]):
            aint = inttime.m_data[cd.m_type][x]
            #v = self.m_data[k][x]
            self.m_data[k][x] = im * a1 * (self.m_data[k][x] - a0) * (cint/aint)
            #if x == 0 and y == 0:
            #    print("" + str(a1) + " * (" + str(v) + " - " + \
            #            str(a0) + ") * (" + str(cint) + "/" + str(aint) + ") = " + str(self.m_data[x,y]))

    def processOPTIC4(self, cd, immersed):
        #self.m_data = self.m_data.astype(float)
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        cint = float(cd.m_coefficients[3])
        k = cd.m_id
        aint = 1
        for x in range(self.m_data.shape[0]):
            self.m_data[k][x] = im * a1 * (self.m_data[k][x] - a0) * (cint/aint)

    def processTHERM1(self, cd):
        return

    def processPOW10(self, cd, immersed):
        #self.m_data = self.m_data.astype(float)
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        k = cd.m_id
        for x in range(self.m_data.shape[0]):
            self.m_data[k][x] = im * pow(10, ((self.m_data[k][x]-a0)/a1))

    def processPOLYU(self, cd):
        #self.m_data = self.m_data.astype(float)
        k = cd.m_id
        for x in range(self.m_data.shape[0]):
            num = 0
            for i in range(0, len(cd.m_coefficients)):
                a = float(cd.m_coefficients[i])
                num += a * pow(self.m_data[k][x],i)
            self.m_data[k][x] = num

    def processPOLYF(self, cd):
        #self.m_data = self.m_data.astype(float)
        a0 = float(cd.m_coefficients[0])
        k = cd.m_id
        for x in range(self.m_data.shape[0]):
            num = a0
            for a in cd.m_coefficients[1:]:
                num *= (self.m_data[k][x] - float(a))
            self.m_data[k][x] = num

    def processDDMM(self, cd):
        return
        #for x in np.nditer(self.m_data, flags=['external_loop'], op_flags=['readwrite']):
            #s = "{:.2f}".format(x)
            #x[...] = s[:1] + " " + s[1:3] + "\' " + s[3:5] + "\""

    def processHHMMSS(self, cd):
        return
        #for x in range(self.m_data.shape[0]):
            #for y in range(self.m_data.shape[1]):
                #s = "{:.2f}".format(self.m_data[x,y])
                #self.m_data[x,y] = s[:2] + "/" + s[2:4] + "/" + s[4:]
        #for x in np.nditer(self.m_data, flags=['external_loop'], op_flags=['readwrite']):
            #print(x)
            #s = "{:.2f}".format(x)
            #x[...] = s[:2] + ":" + s[2:4] + ":" + s[4:6] + "." + s[6:8]

    def processDDMMYY(self, cd):
        return
        #for x in np.nditer(self.m_data, flags=['external_loop'], op_flags=['readwrite']):
            #s = str(x)
            #x[...] = s[:2] + "/" + s[2:4] + "/" + s[4:]

    def processTIME2(self, cd):
        return
        #for x in np.nditer(self.m_data, flags=['external_loop'], op_flags=['readwrite']):
            #x[...] = datetime.fromtimestamp(x).strftime("%y-%m-%d %H:%M:%S")



