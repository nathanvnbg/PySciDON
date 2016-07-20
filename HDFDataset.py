
import collections
import sys

from pyhdf.HDF import *
from pyhdf.V import *
from pyhdf.VS import *

import h5py
import numpy as np


class HDFDataset:
    def __init__(self):
        self.m_id = ""
        self.m_attributes = collections.OrderedDict()
        self.m_columns = collections.OrderedDict()
        self.m_data = None


    def copy(self, ds):
        self.copyAttributes(ds)
        self.m_data = np.copy(ds.m_data)

    def copyAttributes(self, ds):
        for k,v in ds.m_attributes.items():
            self.m_attributes[k] = v

#    def getData(self, name='NONE'):
#        return self.m_data[name]

#    def setData(self, name, data):
#        self.m_data[name] = data


    def printd(self):
        print("Dataset:", self.m_id)
        #self.datasetToColumns()
        #self.datasetToColumns2()
        #self.columnsToDataset()
        #for k in self.m_attributes:
        #    print(k, self.m_attributes[k])
        #print(self.m_data)
        #for d in self.m_data:
        #    print(d)


    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        self.m_id = name
        for k in f.attrs.keys():
            if type(f.attrs[k]) == np.ndarray:
                #print(f.attrs[k])
                #print(type(f.attrs[k].tolist()[0]))
                if type(f.attrs[k].tolist()[0]) == bytes:
                    self.m_attributes[k] = [k.decode("utf-8") for k in f.attrs[k]]
                    #print("Attr:", self.m_attributes[k])
                else:
                    self.m_attributes[k] = [k for k in f.attrs[k]]

            else:
                if type(f.attrs[k]) == bytes:
                    self.m_attributes[k] = f.attrs[k].decode("utf-8")
                else:
                    self.m_attributes[k] = f.attrs[k]
        #print(f)
        #print(type(f[:]))
        self.m_data = f[:] # Convert to numpy.ndarray
        #print("Dataset:", name)
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


    # Writing to HDF4 file using PyHdf
    def writeHDF4(self, vg, vs):
        if self.m_data is not None:
            try:
                name = self.m_id.encode('utf-8')
                dt = []
                #print(self.m_data.dtype)
                for (k,v) in [(x,y[0]) for x,y in sorted(self.m_data.dtype.fields.items(),key=lambda k: k[1])]:
                    #print("type",k,v)
                    if v == np.float64:
                        dt.append((k, HC.FLOAT32, 1))
                        #print("float")
                    if v == np.dtype('S1'):
                        # ToDo: set to correct length
                        # Note: strings of length 1 are not supported
                        dt.append((k, HC.CHAR8, 2))
                        #print("char8")
                #print(dt)

                vd = vs.create(name, dt)

                records = []
                for x in range(self.m_data.shape[0]):
                    rec = []
                    for t in dt:
                        item = self.m_data[t[0]][x]
                        rec.append(item)
                    records.append(rec)
                #print(records)
                vd.write(records)
                vg.insert(vd)

            except:
                print("HDFDataset Error:", sys.exc_info()[0])
            finally:
                vd.detach()

        else:
            print("Dataset.write(): Data is None")


    def getColumn(self, name):
        return self.m_columns[name]

    def appendColumn(self, name, val):
        if name not in self.m_columns:
            self.m_columns[name] = [val]
        else:
            self.m_columns[name].append(val)

    # Converts numpy array into columns (stored as a dictionary)
    def datasetToColumns(self):
        self.m_columns = collections.OrderedDict()
        for k in [k for k,v in sorted(self.m_data.dtype.fields.items(), key=lambda k: k[1])]:
            #print("type",type(ltData.m_data[k]))
            self.m_columns[k] = self.m_data[k].tolist()

    # Convert Prosoft format numpy array to columns    
    def datasetToColumns2(self):
        self.m_columns = collections.OrderedDict()
        ids = self.m_attributes["ID"]
        for k in ids:
            self.m_columns[k] = []
        for k in ids:
            self.m_columns[k].append(self.m_data[0][ids.index(k)])
        

    # Converts columns into numpy array
    def columnsToDataset(self):
        #print("Id:", self.m_id, ", Columns:", self.m_columns)
        #dtype0 = np.dtype([(name, type(ds.m_columns[name][0])) for name in ds.m_columns.keys()])
        dtype = []
        for name in self.m_columns.keys():

            # Numpy dtype column name cannot be unicode in Python 2
            if sys.version_info[0] < 3:
                name = name.encode('utf-8')
        
            item = self.m_columns[name][0]
            if isinstance(item, bytes):
                #dtype.append((name, h5py.special_dtype(vlen=str)))
                dtype.append((name, "|S" + str(len(item))))
                #dtype.append((name, np.dtype(str)))
            # Note: hdf4 only supports 32 bit int, convert to float64
            elif isinstance(item, int):
                dtype.append((name, np.float64))
            else:
                dtype.append((name, type(item)))

        #shape = (len(list(ds.m_columns.values())[0]), len(ds.m_columns))
        shape = (len(list(self.m_columns.values())[0]), )
        #print("Id:", self.m_id)
        #print("Dtype:", dtype)
        #print("Shape:", shape)
        self.m_data = np.empty(shape, dtype=dtype)
        for k,v in self.m_columns.items():
            self.m_data[k] = v

