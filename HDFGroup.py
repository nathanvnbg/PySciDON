
import collections
import sys

# For testing HDF4 support with pyhdf
#from pyhdf.HDF import *
#from pyhdf.V import *
#from pyhdf.VS import *

import h5py
import numpy as np
#import scipy as sp


from HDFDataset import HDFDataset
#from Utilities import Utilities


class HDFGroup:
    def __init__(self):
        self.m_id = ""
        self.m_datasets = collections.OrderedDict()
        self.m_attributes = collections.OrderedDict()


    def copy(self, gp):
        self.copyAttributes(gp)
        for k, ds in gp.m_datasets.items():
            newDS = self.addDataset(ds.m_id)
            newDS.copy(ds)

    def copyAttributes(self, gp):
        for k,v in gp.m_attributes.items():
            self.m_attributes[k] = v


    def addDataset(self, name):
        if len(name) == 0:
            print("Name is 0")
            exit(1)
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
        return None


    # Generates Head attributes
    # ToDo: This should get generated from contect file instead
    def getTableHeader(self, name):
        if name != "None":
            cnt = 1
            ds = self.getDataset(name)
            if ds is None:
                ds = self.addDataset(name)
            for item in ds.m_columns:
                self.m_attributes["Head_"+str(cnt)] = name + " 1 1 " + item
                cnt += 1



    def printd(self):
        print("Group:", self.m_id)
        #print("Sensor Type:", self.m_sensorType)
        print("Frame Type:", self.m_attributes["FrameType"])
        for k in self.m_attributes:
            print("Attribute:", k, self.m_attributes[k])
        #    attr.printd()
        #for gp in self.m_groups:
        #    gp.printd()
        for k in self.m_datasets:
            ds = self.m_datasets[k]
            ds.printd()


    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        #if len(name) == 0:
        #    name = "/"
        self.m_id = name

        #print("Attributes:", [k for k in f.attrs.keys()])
        for k in f.attrs.keys():
            if type(f.attrs[k]) == np.ndarray:
                self.m_attributes[k] = f.attrs[k]
            else: # string
                self.m_attributes[k] = f.attrs[k].decode("utf-8")
        for k in f.keys():
            item = f.get(k)
            if isinstance(item, h5py.Group):
                print("HDFGroup should not contain groups")
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


    # Writing to HDF4 file using PyHdf
    def writeHDF4(self, v, vs):
        print("Group:", self.m_id)
        name = self.m_id[:self.m_id.find("_")]
        if sys.version_info[0] < 3:
            #vg = v.create(self.m_id.encode('utf-8'))
            vg = v.create(name.encode('utf-8'))
        else:
            #vg = v.create(self.m_id)
            vg = v.create(name)

        for k in self.m_attributes:
            attr = vg.attr(k)
            attr.set(HC.CHAR8, self.m_attributes[k])

        for key,ds in self.m_datasets.items():
            #f.create_dataset(ds.m_id, data=np.asarray(ds.m_data))
            ds.writeHDF4(vg, vs)

