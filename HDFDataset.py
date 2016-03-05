
from datetime import datetime

import h5py
import numpy as np

class HDFDataset:
    def __init__(self):
        self._id = ""
        self._attributes = []
        self._data = None
        self._temp = []

    def prnt(self):
        print("Dataset:", self._id)
        for attr in self._attributes:
            print(attr[0], attr[1])
        #for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
        #    x[...] *= 2
            #print(x)
        #print(self._data)
        #for d in self._data:
        #    d.prnt()

    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        self._id = name
        #print(name)
        self._data = np.array(f)

    def write(self, f):
        #print(self._data)
        f.create_dataset(self._id, data=self._data)

    def processL1a(self, cd):
        print(cd._fitType)


    def processOPTIC1(self, cd):
        return

    def processOPTIC2(self, cd, immersed):
        a0 = cd._coefficients[0]
        a1 = cd._coefficients[1]
        im = cd._coefficients[2] if immersed else 1.0
        for x in xrange(self._data.shape[0]):
            for y in xrange(self._data.shape[1]):
                self._data[x,y] = im * a1 * (x - a0)

    def processOPTIC3(self, cd, immersed):
        a0 = cd._coefficients[0]
        a1 = cd._coefficients[1]
        im = cd._coefficients[2] if immersed else 1.0
        cint = cd._coefficients[3]
        for x in xrange(self._data.shape[0]):
            aint = 1
            for y in xrange(self._data.shape[1]):
                self._data[x,y] = im * a1 * (x - a0) * (cint/aint)

    def processOPTIC4(self, cd, immersed):
        a0 = cd._coefficients[0]
        a1 = cd._coefficients[1]
        im = cd._coefficients[2] if immersed else 1.0
        cint = cd._coefficients[3]
        for x in xrange(self._data.shape[0]):
            aint = 1
            for y in xrange(self._data.shape[1]):
                self._data[x,y] = im * a1 * (x - a0) * (cint/aint)

    def processTHERM1(self, cd):
        return

    def processPOW10(self, cd, immersed):
        a0 = cd._coefficients[0]
        a1 = cd._coefficients[1]
        im = cd._coefficients[2] if immersed else 1.0
        for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
            x[...] = im * pow(10, ((x-a0)/a1))

    def processPOLYU(self, cd):
        for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
            num = 0
            for i in range(0, len(cd._coefficients)):
                a = cd._coefficients[i]
                num += a * pow(x,i)
            x[...] = num

    def processPOLYF(self, cd):
        a0 = cd._coefficients[0]
        for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
            num = a0
            for a in cd._coefficients[1:]:
                num *= (x - a)
            x[...] = num

    def processDDMM(self):
        for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
            s = "{:.2f}".format(x)
            x[...] = s[:1] + " " + s[1:3] + "\' " + s[3:5] + "\""

    def processHHMMSS(self):
        for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
            s = "{:.2f}".format(x)
            x[...] = s[:2] + ":" + s[2:4] + ":" + s[4:6] + "." + s[6:8]

    def processDDMMYY(self):
        for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
            s = str(x)
            x[...] = s[:2] + "/" + s[2:4] + "/" + s[4:]

    def processTIME2(self):
        for x in np.nditer(self._data, flags=['external_loop'], op_flags=['readwrite']):
            x[...] = datetime.fromtimestamp(x).strftime("%y-%m-%d %H:%M:%S")

        
        
