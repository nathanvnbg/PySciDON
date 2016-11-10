
import collections
import sys

# For testing HDF4 support with pyhdf
#from pyhdf.HDF import *
#from pyhdf.SD import *
#from pyhdf.V import *
#from pyhdf.VS import *

import h5py
import numpy as np
#import scipy as sp

from HDFGroup import HDFGroup
from HDFDataset import HDFDataset


class HDFRoot:
    def __init__(self):
        self.m_id = ""
        self.m_groups = []
        self.m_attributes = collections.OrderedDict()


    # Creates a copy
    def copy(self, node):
        self.copyAttributes(node)
        for gp in node.m_groups:
            newGP = self.addGroup(gp.m_id)
            newGP.copy(gp)

    def copyAttributes(self, node):
        for k,v in node.m_attributes.items():
            self.m_attributes[k] = v


    def addGroup(self, name):
        gp = None
        if not self.hasGroup(name):
            gp = HDFGroup()
            gp.m_id = name
            self.m_groups.append(gp)
        return gp

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


    def printd(self):
        print("Root:", self.m_id)
        #print("Processing Level:", self.m_processingLevel)
        #for k in self.m_attributes:
        #    print("Attribute:", k, self.m_attributes[k])
        for gp in self.m_groups:
            gp.printd()


    @staticmethod
    def readHDF5(fp):
        root = HDFRoot()
        with h5py.File(fp, "r") as f:

            # set name to text after last '/'
            name = f.name[f.name.rfind("/")+1:]
            if len(name) == 0:
                name = "/"
            root.m_id = name

            # Read attributes
            #print("Attributes:", [k for k in f.attrs.keys()])
            for k in f.attrs.keys():
                root.m_attributes[k] = f.attrs[k].decode("utf-8")
                # Use the following when using h5toh4 converter:
                #root.m_attributes[k.replace("__GLOSDS", "")] = f.attrs[k].decode("utf-8")
            # Read groups
            for k in f.keys():
                item = f.get(k)
                #print(item)
                if isinstance(item, h5py.Group):
                    gp = HDFGroup()
                    root.m_groups.append(gp)
                    gp.read(item)
                elif isinstance(item, h5py.Dataset):
                    print("HDFRoot should not contain datasets")

        return root


    # Writing to HDF5 file
    def writeHDF5(self, fp):
        with h5py.File(fp, "w") as f:
            #print("Root:", self.m_id)
            # Write attributes
            for k in self.m_attributes:
                f.attrs[k] = np.string_(self.m_attributes[k])
                # h5toh4 converter requires "__GLOSDS" to be appended
                # to attribute name for it to be recognized correctly:
                #f.attrs[k+"__GLOSDS"] = np.string_(self.m_attributes[k])
            # Write groups
            for gp in self.m_groups:
                gp.write(f)

    # Writing to HDF4 file using PyHdf
    def writeHDF4(self, fp):
        try:
            hdfFile = HDF(fp, HC.WRITE|HC.CREATE)
            sd = SD(fp, SDC.WRITE)
            v = hdfFile.vgstart()
            vs = hdfFile.vstart()

            for k in self.m_attributes:
                #print(k, self.m_attributes[k])
                attr = sd.attr(k)
                attr.set(SDC.CHAR8, self.m_attributes[k])

            for gp in self.m_groups:
                gp.writeHDF4(v, vs)
        except:
            print("HDFRoot Error:", sys.exc_info()[0])
        finally:
            vs.end()
            v.end()
            sd.end()
            hdfFile.close()

