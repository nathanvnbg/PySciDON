
import collections

import h5py
import numpy as np
#import scipy as sp
from scipy import interpolate

from HDFDataset import HDFDataset

class HDFGroup:
    def __init__(self):
        self.m_id = ""
        self.m_datasets = {}
        self.m_attributes = collections.OrderedDict()
        self.m_sensorType = ""
        self.m_frameType = ""


    def addDataset(self, name):
        ds = None
        if not self.hasDataset(name):
            ds = HDFDataset()
            ds.m_id = name
            self.m_datasets[name] = ds
        return ds

    def hasDataset(self, name):
        return (name in self.m_datasets)

    def getDataset(self, name):
        if self.hasDataset(name):
            return self.m_datasets[name]
        ds = HDFDataset()
        ds.m_id = name
        self.m_datasets[name] = ds
        return ds


    def prnt(self):
        print("Group:", self.m_id)
        print("Sensor Type:", self.m_sensorType)
        print("Frame Type:", self.m_frameType)
        for k in self.m_attributes:
            print("Attribute:", k, self.m_attributes[k])
        #    attr.prnt()
        #for gp in self.m_groups:
        #    gp.prnt()
        for ds in self.m_datasets:
            ds.prnt()


    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        #if len(name) == 0:
        #    name = "/"
        self.m_id = name

        #print("Attributes:", [k for k in f.attrs.keys()])
        for k in f.attrs.keys():
            self.m_attributes[k] = f.attrs[k].decode("utf-8")
        for k in f.keys():
            item = f.get(k)
            if isinstance(item, h5py.Group):
                print("HDFRoot should not contain groups")
            elif isinstance(item, h5py.Dataset):
                #print("Item:", k)
                ds = HDFDataset()
                self.m_datasets[k] = ds
                ds.read(item)


    def write(self, f):
        #print("Group:", self.m_id)
        f = f.create_group(self.m_id)
        for k in self.m_attributes:
            f.attrs[k] = np.string_(self.m_attributes[k])
        for key,ds in self.m_datasets.items():
            #f.create_dataset(ds.m_id, data=np.asarray(ds.m_data))
            ds.write(f)


    def getStartTime(self, time = 999999):
        if self.hasDataset("TIMER"):
            ds = self.getDataset("TIMER")
            if ds.m_data is not None:
                #print(ds.m_data.dtype)
                t = float(ds.m_data["NONE"][0])
                if t < time:
                    time = t
        return time

    def processTIMER(self, time):
        if self.hasDataset("TIMER"):
            ds = self.getDataset("TIMER")
            if ds.m_data is not None:
                #print("Time:", time)
                #print(ds.m_data)
                for i in range(0, len(ds.m_data)):
                    ds.m_data["NONE"][i] -= time
                #print(ds.m_data)
        return time


    def processL1a(self, cf):
        inttime = None
        for cd in cf.m_data:
            if cd.m_type == "INTTIME":
                #print("Process INTTIME")
                ds = self.getDataset("INTTIME")
                ds.processL1a(cd)
                inttime = ds

        for cd in cf.m_data:
            if self.hasDataset(cd.m_type) and cd.m_type != "INTTIME":
                #print("Dataset:", cd.m_type)
                ds = self.getDataset(cd.m_type)
                ds.processL1a(cd, inttime)

