
import h5py
import numpy as np

class HDFDataset:
    def __init__(self):
        self._id = b""
        self._attributes = []
        self._data = []

    def prnt(self):
        print("Dataset:", self._id)
        for attr in self._attributes:
            print(attr[0], attr[1])
        #print(self._data)
        #for d in self._data:
        #    d.prnt()

    def read(self, f):
        name = f.name[f.name.rfind("/")+1:]
        self._id = bytes(name, "utf-8")
        #print(name)
        self._data = np.array(f).tolist()

    def write(self, f):
        f.create_dataset(self._id, data=np.asarray(self._data))
