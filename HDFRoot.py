
import collections

import h5py
import numpy as np
#import scipy as sp
from scipy import interpolate

from HDFGroup import HDFGroup
from HDFDataset import HDFDataset

class HDFRoot:
    def __init__(self):
        self.m_id = ""
        self.m_groups = []
        self.m_attributes = collections.OrderedDict()

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
            self.m_attributes[k] = f.attrs[k].decode("utf-8")
        for k in f.keys():
            item = f.get(k)
            #print(item)
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
            f.attrs[k] = np.string_(self.m_attributes[k])
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


    def processL1a(self, calibrationMap):
        for gp in self.m_groups:
            cf = calibrationMap[gp.m_attributes["FrameTag"]]
            #print(gp.m_id, gp.m_attributes)
            print("File:", cf.m_id)
            gp.processL1a(cf)


    def lerp(self, x, xa, xb, ya, yb):
        return (ya + (yb - ya) * (x - xa) / (xb - xa))

    def processDarkColumn(self, k, darkData, darkTimer, lightTimer, newDarkData):
        #print(darkTimer.m_data)
        x = darkTimer.m_data["NONE"]
        y = darkData.m_data[k]
        new_x = lightTimer.m_data["NONE"]
        new_y = interpolate.interp1d(x, y, kind='linear', bounds_error=False)(new_x)

        test = False
        for i in range(len(new_y)):
            if np.isnan(new_y[i]):
                #print("NaN")
                if test:
                    new_y[i] = darkData.m_data[k][darkData.m_data.shape[0]-1]
                else:
                    new_y[i] = darkData.m_data[k][0]
            else:
                test = True

        newDarkData[k] = new_y

        '''
        dt0 = darkTimer.m_data["NONE"][0]
        dtMax = darkTimer.m_data["NONE"][darkTimer.m_data.shape[0]-1]
        for x in range(lightTimer.m_data.shape[0]):
            lt = lightTimer.m_data["NONE"][x]
            #print(lightTimer.m_data[x,0])
            if lt < dt0:
                newDarkData[k][x] = darkData.m_data[k][0]
            elif lt > dtMax:
                newDarkData[k][x] = darkData.m_data[k][darkData.m_data.shape[0]-1]
            else:
                for i in range(darkTimer.m_data.shape[0]-1):
                    t0 = darkTimer.m_data["NONE"][i]
                    t1 = darkTimer.m_data["NONE"][i+1]
                    if lt > t0 and lt < t1:
                        d0 = darkData.m_data[k][i]
                        d1 = darkData.m_data[k][i+1]
                        newDarkData[k][x] = self.lerp(lt, t0, t1, d0, d1)
                        break
        '''



    def processDarkCorrection(self, sensorType):
        darkData = None
        darkTimer = None
        lightData = None
        lightTimer = None

        for gp in self.m_groups:
            if gp.m_frameType == "ShutterDark" and gp.hasDataset(sensorType):
                darkData = gp.getDataset(sensorType)
                darkTimer = gp.getDataset("TIMER")

            if gp.m_frameType == "ShutterLight" and gp.hasDataset(sensorType):
                lightData = gp.getDataset(sensorType)
                lightTimer = gp.getDataset("TIMER")

        if (darkData == None) or (lightData == None):
            print("Dark Correction, dataset not found:", darkData, lightData)
            return

        # Interpolate Dark Dataset to match number of elements as Light Dataset
        #print(len(darkData.m_data), len(lightData.m_data))
        #print(lightData.m_data)    

        newDarkData = np.copy(lightData.m_data)

        #print(darkData.m_data.dtype.fields.keys())
        #for y in range(darkData.m_data.shape[1]):
        for k in darkData.m_data.dtype.fields.keys():
            self.processDarkColumn(k, darkData, darkTimer, lightTimer, newDarkData)

        print(lightData.m_data.shape)
        print(newDarkData.shape)
        darkData.m_data = newDarkData

        # Get corrected data by subtract interpolated dark data from light data
        #for x in range(lightData.m_data.shape[0]):
        #    for y in range(lightData.m_data.shape[1]):
        #        lightData.m_data[x,y] -= newDarkData[x,y]

        for k in lightData.m_data.dtype.fields.keys():
            for x in range(lightData.m_data.shape[0]):
                lightData.m_data[k][x] -= newDarkData[k][x]

        #print(lightData.m_data)


    def processL2(self):
        self.processDarkCorrection("ES")
        self.processDarkCorrection("LI")
        self.processDarkCorrection("LT")


    def interpolateGPSData(self, esGroup, gpsGroup):
        print("Interpolate GPS Data")
        esData = esGroup.getDataset("ES")
        esDateData = esGroup.getDataset("DATETAG")
        esTimeData = esGroup.getDataset("TIMETAG2")
        
        for k in esData.m_data.dtype.fields.keys():
            print(k)
        
        #x = darkTimer.m_data["NONE"]
        #y = darkData.m_data[k]
        #new_x = lightTimer.m_data["NONE"]
        #new_y = sp.interpolate.interp1d(x, y, kind='linear', bounds_error=False)(new_x)
        

    def interpolateSASData(self, liGroup, ltGroup):
        print("Interpolate SAS Data")

    def processL2s(self, node):
        esGroup = None
        gpsGroup = None
        liGroup = None
        ltGroup = None
        for gp in self.m_groups:
            if gp.m_id.startswith("GPS"):
                print("GPS")
                gpsGroup = gp
            elif gp.hasDataset("ES") and gp.m_frameType == "ShutterLight":
                print("ES")
                esGroup = gp
            elif gp.hasDataset("LI") and gp.m_frameType == "ShutterLight":
                print("LI")
                liGroup = gp
            elif gp.hasDataset("LT") and gp.m_frameType == "ShutterLight":
                print("LT")
                ltGroup = gp

        node.interpolateGPSData(esGroup, gpsGroup)
        node.interpolateSASData(esGroup, gpsGroup)
        
        
        
