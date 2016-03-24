
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
            #self.m_attributes[k] = f.attrs[k].decode("utf-8")
            self.m_attributes[k.replace("__GLOSDS", "")] = f.attrs[k].decode("utf-8")
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
            #f.attrs[k] = np.string_(self.m_attributes[k])
            f.attrs[k+"__GLOSDS"] = np.string_(self.m_attributes[k])
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


    def processL1b(self, calibrationMap):
        self.m_attributes["PROCESSING_LEVEL"] = "1b"
        
        cf = calibrationMap["SATHSE0150"]
        esUnits = cf.getUnits("ES")
        cf = calibrationMap["SATHSL0151"]
        luUnits = cf.getUnits("LI")

        self.m_attributes["LU_UNITS"] = luUnits
        self.m_attributes["ED_UNITS"] = esUnits
        self.m_attributes["ES_UNITS"] = esUnits
        
        for gp in self.m_groups:
            cf = calibrationMap[gp.m_attributes["FrameTag"]]
            #print(gp.m_id, gp.m_attributes)
            print("File:", cf.m_id)
            gp.processL1b(cf)


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
            if gp.m_attributes["FrameType"] == "ShutterDark" and gp.hasDataset(sensorType):
                darkData = gp.getDataset(sensorType)
                darkTimer = gp.getDataset("TIMER")

            if gp.m_attributes["FrameType"] == "ShutterLight" and gp.hasDataset(sensorType):
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
        self.m_attributes["PROCESSING_LEVEL"] = "2"
        self.m_attributes["DEGLITCH_PRODAT"] = "OFF"
        self.m_attributes["DEGLITCH_REFDAT"] = "OFF"
        self.processDarkCorrection("ES")
        self.processDarkCorrection("LI")
        self.processDarkCorrection("LT")




    def utcToSec(self, utc):
        t = str(int(utc))
        #print(s)
        #print(s[:2], s[2:4], s[4:])
        h = int(t[:2])
        m = int(t[2:4])
        s = int(t[4:])
        return ((h*60)+m)*60+s

    def secToTimeTag2(self, sec):
        #return float(time.strftime("%H%M%S", time.gmtime(sec)))
        t = sec * 1000
        s, ms = divmod(t, 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return float("%d%02d%02d%03d" % (h, m, s, ms))
    
    def timeTag2ToSec(self, time):
        t = str(int(time))
        h = int(t[:2])
        m = int(t[2:4])
        s = int(t[4:6])
        ms = int(t[6:])
        return ((h*60)+m)*60+s+(float(ms)/1000.0)


    def interpolateSpline(self, xData, xTimer, yTimer, newXData):
        x = xTimer
        new_x = yTimer

        for k in [x for x,y in sorted(xData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
            y = xData.m_data[k]
            newXData.m_columns[k] = interpolate.interp1d(x, y, kind='cubic', bounds_error=False)(new_x)

            test = False
            for i in range(len(newXData.m_columns[k])):
                if np.isnan(newXData.m_columns[k][i]):
                    #print("NaN")
                    if test:
                        newXData.m_columns[k][i] = xData.m_data[k][xData.m_data.shape[0]-1]
                    else:
                        newXData.m_columns[k][i] = xData.m_data[k][0]
                else:
                    test = True


    def interpolateLinear(self, xData, xTimer, yTimer, newXData):
        x = xTimer
        new_x = yTimer

        for k in [x for x,y in sorted(xData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
            y = xData.m_data[k]
            newXData.m_columns[k] = interpolate.interp1d(x, y, kind='linear', bounds_error=False)(new_x)

            test = False
            for i in range(len(newXData.m_columns[k])):
                if np.isnan(newXData.m_columns[k][i]):
                    #print("NaN")
                    if test:
                        newXData.m_columns[k][i] = xData.m_data[k][xData.m_data.shape[0]-1]
                    else:
                        newXData.m_columns[k][i] = xData.m_data[k][0]
                else:
                    test = True


    # interpolate GPS to match ES using linear interpolation
    def interpolateGPSData(self, node, esGroup, gpsGroup):
        print("Interpolate GPS Data2")

        # ES
        esData = esGroup.getDataset("ES")
        esDateData = esGroup.getDataset("DATETAG")
        esTimeData = esGroup.getDataset("TIMETAG2")

        refGroup = node.getGroup("Reference")
        newESData = refGroup.addDataset("ES_hyperspectral")

        newESData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
        newESData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
        for k in [x for x,y in sorted(esData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
            #print("type",type(esData.m_data[k]))
            newESData.m_columns[k] = esData.m_data[k].tolist()
        newESData.columnsToDataset()


        # GPS
        gpsTimeData = gpsGroup.getDataset("UTCPOS")
        gpsCourseData = gpsGroup.getDataset("COURSE")
        gpsLatPosData = gpsGroup.getDataset("LATPOS")
        gpsLonPosData = gpsGroup.getDataset("LONPOS")
        gpsMagVarData = gpsGroup.getDataset("MAGVAR")
        gpsSpeedData = gpsGroup.getDataset("SPEED")

        gpsGroup = node.getGroup("GPS")
        newGPSCourseData = gpsGroup.addDataset("COURSE")
        newGPSLatPosData = gpsGroup.addDataset("LATPOS")
        newGPSLonPosData = gpsGroup.addDataset("LONPOS")
        newGPSMagVarData = gpsGroup.addDataset("MAGVAR")
        newGPSSpeedData = gpsGroup.addDataset("SPEED")

        newGPSCourseData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
        newGPSCourseData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
        newGPSLatPosData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
        newGPSLatPosData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
        newGPSLonPosData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
        newGPSLonPosData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
        newGPSMagVarData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
        newGPSMagVarData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()
        newGPSSpeedData.m_columns["Datetag"] = esDateData.m_data["NONE"].tolist()
        newGPSSpeedData.m_columns["Timetag2"] = esTimeData.m_data["NONE"].tolist()


        xTimer = []
        for i in range(gpsTimeData.m_data.shape[0]):
            xTimer.append(self.utcToSec(gpsTimeData.m_data["NONE"][i]))
    
        yTimer = []
        for i in range(esTimeData.m_data.shape[0]):
            yTimer.append(self.timeTag2ToSec(esTimeData.m_data["NONE"][i]))


        # Interpolate
        self.interpolateLinear(gpsCourseData, xTimer, yTimer, newGPSCourseData)
        self.interpolateLinear(gpsLatPosData, xTimer, yTimer, newGPSLatPosData)
        self.interpolateLinear(gpsLonPosData, xTimer, yTimer, newGPSLonPosData)
        self.interpolateLinear(gpsMagVarData, xTimer, yTimer, newGPSMagVarData)
        self.interpolateLinear(gpsSpeedData, xTimer, yTimer, newGPSSpeedData)


        newGPSCourseData.columnsToDataset()
        newGPSLatPosData.columnsToDataset()
        newGPSLonPosData.columnsToDataset()
        newGPSMagVarData.columnsToDataset()
        newGPSSpeedData.columnsToDataset()


        #x = darkTimer.m_data["NONE"]
        #y = darkData.m_data[k]
        #new_x = lightTimer.m_data["NONE"]
        #new_y = sp.interpolate.interp1d(x, y, kind='linear', bounds_error=False)(new_x)


    # interpolate LT to match LI using spline interpolation
    def interpolateSASData(self, node, liGroup, ltGroup):
        print("Interpolate SAS Data2")
    
        # LI
        liData = liGroup.getDataset("LI")
        liDateData = liGroup.getDataset("DATETAG")
        liTimeData = liGroup.getDataset("TIMETAG2")
    
        sasGroup = node.getGroup("SAS")
        newLIData = sasGroup.addDataset("LI_hyperspectral")
        newLTData = sasGroup.addDataset("LT_hyperspectral")
    
    
        newLIData.m_columns["Datetag"] = liDateData.m_data["NONE"].tolist()
        newLIData.m_columns["Timetag2"] = liTimeData.m_data["NONE"].tolist()
        for k in [x for x,y in sorted(liData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
            #print("type",type(esData.m_data[k]))
            newLIData.m_columns[k] = liData.m_data[k].tolist()
        newLIData.columnsToDataset()
    
    
        # LT
        ltTimeData = ltGroup.getDataset("TIMETAG2")
        ltData = ltGroup.getDataset("LT")
    
        newLTData.m_columns["Datetag"] = liDateData.m_data["NONE"].tolist()
        newLTData.m_columns["Timetag2"] = liTimeData.m_data["NONE"].tolist()
    
    
        xTimer = []
        for i in range(ltTimeData.m_data.shape[0]):
            xTimer.append(self.timeTag2ToSec(ltTimeData.m_data["NONE"][i]))
    
        yTimer = []
        for i in range(liTimeData.m_data.shape[0]):
            yTimer.append(self.timeTag2ToSec(liTimeData.m_data["NONE"][i]))
    
    
        # interpolate
        self.interpolateSpline(ltData, xTimer, yTimer, newLTData)
    
        newLTData.columnsToDataset()


    def processL2s(self):

        root2s = HDFRoot()
        root2s.copyAttributes(self)
        root2s.m_attributes["PROCESSING_LEVEL"] = "2s"
        root2s.m_attributes["DEPTH_RESOLUTION"] = "0.1 m"

        root2s.addGroup("GPS")
        root2s.addGroup("Reference")
        root2s.addGroup("SAS")

        esGroup = None
        gpsGroup = None
        liGroup = None
        ltGroup = None
        for gp in self.m_groups:
            if gp.m_id.startswith("GPS"):
                print("GPS")
                gpsGroup = gp
            elif gp.hasDataset("ES") and gp.m_attributes["FrameType"] == "ShutterLight":
                print("ES")
                esGroup = gp
            elif gp.hasDataset("LI") and gp.m_attributes["FrameType"] == "ShutterLight":
                print("LI")
                liGroup = gp
            elif gp.hasDataset("LT") and gp.m_attributes["FrameType"] == "ShutterLight":
                print("LT")
                ltGroup = gp

        self.interpolateGPSData(root2s, esGroup, gpsGroup)
        self.interpolateSASData(root2s, liGroup, ltGroup)
    
        return root2s

