
import collections

import h5py
import numpy as np

from HDFGroup import HDFGroup
from HDFDataset import HDFDataset

class HDFRoot:
    def __init__(self):
        self.m_id = ""
        self.m_groups = []
        self.m_attributes = collections.OrderedDict()


    def hasGroup(self, name):
        for gp in self.m_groups:
            if gp.m_id == name:
                return True
        return False

    def getGroup(self, name):
        for gp in self.m_groups:
            if gp.m_id == name:
                return gp
        gp = HDFDataset()
        gp.m_id = name
        self.m_groups.append(gp)
        return gp


    def prnt(self):
        print("Root:", self.m_id)
        #print("Processing Level:", self.m_processingLevel)
        #for k in self.m_attributes:
        #    print("Attribute:", k, self.m_attributes[k])
        for gp in self.m_groups:
            gp.prnt()


    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        if len(name) == 0:
            name = "/"
        self.m_id = name

        #print("Attributes:", [k for k in f.attrs.keys()])
        for k in f.attrs.keys():
            self.m_attributes[k] = f.attrs[k]
        for k in f.keys():
            item = f.get(k)
            print(item)
            if isinstance(item, h5py.Group):
                gp = HDFGroup()
                self.m_groups.append(gp)
                gp.read(item)
            elif isinstance(item, h5py.Dataset):
                print("HDFRoot should not contain datasets")
            
        #if isinstance(item, h5py.File):
        #if isinstance(item, h5py.Group):
        #if isinstance(item, h5py.Dataset):
        

    def write(self, f):
        #print("Root:", self.m_id)
        for k in self.m_attributes:
            f.attrs[k] = self.m_attributes[k]
        for gp in self.m_groups:
            gp.write(f)


    def getStartTime(self, time = 999999):
        for gp in self.m_groups:
            #print(gp.m_id)
            t = gp.getStartTime(time)
            if t < time:
                time = t
        return time

    def processTIMER(self):
        time = self.getStartTime()
        print("Time:", time)
        for gp in self.m_groups:
            #print(gp.m_id)
            gp.processTIMER(time)
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



        

