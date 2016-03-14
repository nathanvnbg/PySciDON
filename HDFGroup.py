
import collections

import h5py
import numpy as np

from HDFDataset import HDFDataset

class HDFGroup:
    def __init__(self):
        self._id = ""
        self._attributes = collections.OrderedDict()
        self._groups = []
        self._datasets = []
        self._sensorType = ""
        self._frameType = ""

    def prnt(self):
        print("Group:", self._id)
        print("Sensor Type:", self._sensorType)
        print("Frame Type:", self._frameType)
        for k in self._attributes:
            print("Attribute:", k, self._attributes[k])
        #    attr.prnt()
        for gp in self._groups:
            gp.prnt()
        for ds in self._datasets:
            ds.prnt()

    def hasDataset(self, name):
        for ds in self._datasets:
            if ds._id == name:
                return True
        return False

    def getDataset(self, name):
        for ds in self._datasets:
            if ds._id == name:
                return ds
        ds = HDFDataset()
        ds._id = name
        self._datasets.append(ds)
        return ds
            

    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        if len(name) == 0:
            name = "/"
        #self._id = bytes(name, "utf-8")
        self._id = name

        #print("Attributes:", [k for k in f.attrs.keys()])
        for k in f.attrs.keys():
            self._attributes[k] = f.attrs[k]
        for k in f.keys():
            item = f.get(k)
            if isinstance(item, h5py.Group):
                gp = HDFGroup()
                self._groups.append(gp)
                gp.read(item)
            elif isinstance(item, h5py.Dataset):
                ds = HDFDataset()
                self._datasets.append(ds)
                ds.read(item)
            
        #if isinstance(item, h5py.File):
        #if isinstance(item, h5py.Group):
        #if isinstance(item, h5py.Dataset):
        

    def write(self, f):
        #print("Group:", self._id)
        if self._id != "/":
            f = f.create_group(self._id)
        for k in self._attributes:
            f.attrs[k] = self._attributes[k]
        for gp in self._groups:
            gp.write(f)
        for ds in self._datasets:
            #f.create_dataset(ds._id, data=np.asarray(ds._data))
            ds.write(f)


    def getStartTime(self, time = 999999):
        for gp in self._groups:
            #print(gp._id)
            t = gp.getStartTime(time)
            if t < time:
                time = t
        for ds in self._datasets:
            #print(ds._id)
            if ds._id == "TIMER" and ds._data != None:
                #print(ds._data)
                t = float(ds._data[0])
                if t < time:
                    time = t
        return time

    def processTIMER(self):
        time = self.getStartTime()
        print("Time:", time)
        self.processTIMER2(time)

    def processTIMER2(self, time):
        for gp in self._groups:
            #print(gp._id)
            gp.processTIMER2(time)
        for ds in self._datasets:
            #print(ds._id)
            if ds._id == "TIMER" and ds._data != None:
                #print("Time:", time)
                #print(ds._data)
                for i in range(0, len(ds._data)):
                    ds._data[i] -= time
                #print(ds._data)
        return time


    def processL1a(self, cf):
        inttime = None
        for cd in cf._data:
            if cd._type == "INTTIME":
                #print("Process INTTIME")
                ds = self.getDataset("INTTIME")
                ds.processL1a(cd)
                inttime = ds
            
        for cd in cf._data:
            if self.hasDataset(cd._type) and cd._type != "INTTIME":
                #print("Dataset:", cd._type)
                ds = self.getDataset(cd._type)
                ds.processL1a(cd, inttime)



        

