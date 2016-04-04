
import collections
from datetime import datetime
import sys

from pyhdf.HDF import *
from pyhdf.SD import *
from pyhdf.V import *
from pyhdf.VS import *

import h5py
import numpy as np
#import scipy as sp
from scipy import interpolate

from HDFGroup import HDFGroup
from HDFDataset import HDFDataset

#from CalibrationFileReader import CalibrationFileReader
from RawFileReader import RawFileReader

class HDFRoot:
    def __init__(self):
        self.m_id = ""
        self.m_groups = []
        self.m_attributes = collections.OrderedDict()


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


    def prnt(self):
        print("Root:", self.m_id)
        #print("Processing Level:", self.m_processingLevel)
        #for k in self.m_attributes:
        #    print("Attribute:", k, self.m_attributes[k])
        for gp in self.m_groups:
            gp.prnt()



    #if isinstance(item, h5py.File):
    #if isinstance(item, h5py.Group):
    #if isinstance(item, h5py.Dataset):

    @staticmethod
    def readHDF5(fp):
        root = HDFRoot()
        with h5py.File(fp, "r") as f:

            name = f.name[f.name.rfind("/")+1:]
            if len(name) == 0:
                name = "/"
            root.m_id = name

            #print("Attributes:", [k for k in f.attrs.keys()])
            for k in f.attrs.keys():
                #self.m_attributes[k] = f.attrs[k].decode("utf-8")
                root.m_attributes[k.replace("__GLOSDS", "")] = f.attrs[k].decode("utf-8")
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



    def writeHDF5(self, fp):
        with h5py.File(fp, "w") as f:
            #print("Root:", self.m_id)
            for k in self.m_attributes:
                #f.attrs[k] = np.string_(self.m_attributes[k])
                f.attrs[k+"__GLOSDS"] = np.string_(self.m_attributes[k])
            for gp in self.m_groups:
                gp.write(f)

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


    def processL1a(self, calibrationMap):

        root = HDFRoot()
        root.m_id = "/"
        root.m_attributes["PROSOFT"] = "Prosoft 7.7.16_6"
        root.m_attributes["PROSOFT_INSTRUMENT_CONFIG"] = "testcfg"
        root.m_attributes["PROSOFT_PARAMETERS_FILE_NAME"] = "test.mat"
        root.m_attributes["CAL_FILE_NAMES"] = "HED150E2013.cal,HLD151C2013.cal," \
            "HLD152C2013.cal,HSE150E2013.cal,HSL151C2013.cal,HSL152C2013.cal," \
            "MPR052a.cal,GPRMC_NoMode.TDF"
        root.m_attributes["WAVELENGTH_UNITS"] = "nm"
        root.m_attributes["LU_UNITS"] = "count"
        root.m_attributes["ED_UNITS"] = "count"
        root.m_attributes["ES_UNITS"] = "count"
        root.m_attributes["RAW_FILE_NAME"] = "data.raw"


        contextMap = {}

        contextMap["SATHED0150"] = HDFGroup()
        contextMap["SATHLD0151"] = HDFGroup()
        contextMap["SATHLD0152"] = HDFGroup()
        contextMap["SATHSE0150"] = HDFGroup()
        contextMap["SATHSL0151"] = HDFGroup()
        contextMap["SATHSL0152"] = HDFGroup()
        contextMap["SATSAS0052"] = HDFGroup()
        contextMap["$GPRMC"] = HDFGroup()
        contextMap["SATHED0150"].m_id = "Reference"
        contextMap["SATHLD0151"].m_id = "SAS"
        contextMap["SATHLD0152"].m_id = "SAS"
        contextMap["SATHSE0150"].m_id = "Reference"
        contextMap["SATHSL0151"].m_id = "SAS"
        contextMap["SATHSL0152"].m_id = "SAS"
        contextMap["SATSAS0052"].m_id = "SAS"
        contextMap["$GPRMC"].m_id = "GPS"

        #calibrationMap = CalibrationFileReader.read("cal2013.sip")
        #print("calibrationMap:", list(calibrationMap.keys()))
        root = RawFileReader.readRawFile("data.raw", calibrationMap, contextMap, root)

        root.m_groups.append(contextMap["SATHED0150"])
        root.m_groups.append(contextMap["SATHLD0151"])
        root.m_groups.append(contextMap["SATHLD0152"])
        root.m_groups.append(contextMap["SATHSE0150"])
        root.m_groups.append(contextMap["SATHSL0151"])
        root.m_groups.append(contextMap["SATHSL0152"])
        root.m_groups.append(contextMap["SATSAS0052"])
        root.m_groups.append(contextMap["$GPRMC"])


        root.m_attributes["PROCESSING_LEVEL"] = "1a"
        dt = datetime.now()
        dtstr = dt.strftime("%d-%b-%Y %H:%M:%S")
        root.m_attributes["FILE_CREATION_TIME"] = dtstr

        for gp in root.m_groups:
            for ds in gp.m_datasets.values():
                ds.columnsToDataset()

        RawFileReader.generateContext(root)

        return root


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
        root = HDFRoot()
        root.copy(self)

        root.m_attributes["PROCESSING_LEVEL"] = "1b"
        
        cf = calibrationMap["SATHSE0150"]
        esUnits = cf.getUnits("ES")
        cf = calibrationMap["SATHSL0151"]
        luUnits = cf.getUnits("LI")

        root.m_attributes["LU_UNITS"] = luUnits
        root.m_attributes["ED_UNITS"] = esUnits
        root.m_attributes["ES_UNITS"] = esUnits
        
        for gp in root.m_groups:
            cf = calibrationMap[gp.m_attributes["FrameTag"]]
            #print(gp.m_id, gp.m_attributes)
            print("File:", cf.m_id)
            gp.processL1b(cf)

        return root


    # ToDo: improve later
    def dataDeglitching(self, ds):

        noiseThresh = 20        

        # Copy dataset to dictionary
        columns = collections.OrderedDict()
        for k in [k for k,v in sorted(ds.m_data.dtype.fields.items(), key=lambda k: k[1])]:
            #print("type",type(esData.m_data[k]))
            columns[k] = ds.m_data[k].tolist()

        for k,v in columns.items():
            #print(k,v)
            dS = []
            for i in range(len(v)-1):
                #print(v[i])
                if v[i] != 0:
                    dS.append(v[i+1]/v[i])
            dS_sorted = sorted(dS)
            n1 = 0.2 * len(dS)
            n2 = 0.75 * len(dS)
            #print(dS_sorted)
            stdS = dS_sorted[round(n2)] - dS_sorted[round(n1)]
            medN = np.median(np.array(dS))
            print(n1,n2,stdS,medN)
            for i in range(len(v)):
                if abs(v[i] - medN) > noiseThresh*stdS:
                    v[i] = np.nan

        ds.m_columns = columns
        ds.columnsToDataset()

    def processDataDeglitching(self):
        esDarkGroup = None
        liDarkGroup = None
        ltDarkGroup = None
        for gp in self.m_groups:
            if gp.hasDataset("ES") and gp.m_attributes["FrameType"] == "ShutterDark":
                print("ES")
                esDarkGroup = gp
            elif gp.hasDataset("LI") and gp.m_attributes["FrameType"] == "ShutterDark":
                print("LI")
                liDarkGroup = gp
            elif gp.hasDataset("LT") and gp.m_attributes["FrameType"] == "ShutterDark":
                print("LT")
                ltDarkGroup = gp

        esDarkDataset = esDarkGroup.getDataset("ES")
        self.dataDeglitching(esDarkDataset)

        liDarkDataset = liDarkGroup.getDataset("LI")
        self.dataDeglitching(liDarkDataset)

        ltDarkDataset = ltDarkGroup.getDataset("LT")
        self.dataDeglitching(ltDarkDataset)

    '''
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

    def processDarkColumn(self, k, darkData, darkTimer, lightTimer, newDarkData):
        #print(darkTimer.m_data)
        x = np.copy(darkTimer.m_data["NONE"]).tolist()
        y = np.copy(darkData.m_data[k]).tolist()
        new_x = lightTimer.m_data["NONE"]

        n = len(x)-1
        if new_x[n] > x[n]:
            #print(new_x[n], x[n])
            x.append(new_x[n])
            y.append(y[n])
        if new_x[0] < x[0]:
            #print(new_x[0], x[0])
            x.insert(0, new_x[0])
            y.insert(0, y[0])

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
        root = HDFRoot()
        root.copy(self)
        
        root.m_attributes["PROCESSING_LEVEL"] = "2"
        root.m_attributes["DEGLITCH_PRODAT"] = "OFF"
        root.m_attributes["DEGLITCH_REFDAT"] = "OFF"
        
        #print("Start Time:", root.getStartTime())
        root.processTIMER()
        
        #root.processDataDeglitching()

        root.processDarkCorrection("ES")
        root.processDarkCorrection("LI")
        root.processDarkCorrection("LT")

        return root


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
    
    def timeTag2ToSec(self, tt2):
        t = str(int(tt2))
        h = int(t[:2])
        m = int(t[2:4])
        s = int(t[4:6])
        ms = int(t[6:])
        return ((h*60)+m)*60+s+(float(ms)/1000.0)


    # recalculate TimeTag2 to follow GPS UTC time
    def processGPSTime(self):
        sec = 0

        for gp in self.m_groups:
            if gp.m_id.startswith("GPS"):
                ds = gp.getDataset("UTCPOS")
                sec = self.utcToSec(ds.m_data["NONE"][0])
                #print("GPS UTCPOS:", ds.m_data["NONE"][0], "-> sec:", sec)
                #print(secToUtc(sec))

        for gp in self.m_groups:
            if not gp.m_id.startswith("GPS"):
                dsTimer = gp.getDataset("TIMER")
                dsTimeTag2 = gp.getDataset("TIMETAG2")
                for x in range(dsTimeTag2.m_data.shape[0]):
                    v = dsTimer.m_data["NONE"][x] + sec
                    dsTimeTag2.m_data["NONE"][x] = self.secToTimeTag2(v)


    def interpolateSpline(self, xData, xTimer, yTimer, newXData):
        x = xTimer
        new_x = yTimer

        for k in [k for k,v in sorted(xData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
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

        for k in [k for k,v in sorted(xData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
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
        for k in [k for k,v in sorted(esData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
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
        for k in [k for k,v in sorted(liData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
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

        self.processGPSTime()

        root = HDFRoot()
        root.copyAttributes(self)
        root.m_attributes["PROCESSING_LEVEL"] = "2s"
        root.m_attributes["DEPTH_RESOLUTION"] = "0.1 m"

        root.addGroup("GPS")
        root.addGroup("Reference")
        root.addGroup("SAS")
        
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

        self.interpolateGPSData(root, esGroup, gpsGroup)
        self.interpolateSASData(root, liGroup, ltGroup)
    
        return root


    def interpolateWavelength(self, ds, newDS):

        # Copy dataset to dictionary
        columns = collections.OrderedDict()
        for k in [k for k,v in sorted(ds.m_data.dtype.fields.items(), key=lambda k: k[1])]:
            #print("type",type(esData.m_data[k]))
            columns[k] = ds.m_data[k].tolist()
        saveDatetag = columns.pop("Datetag")
        saveTimetag2 = columns.pop("Timetag2")


        # Get wavelength values
        wavelength = []
        for k in columns:
            #print(k)
            wavelength.append(float(k))
        x = np.asarray(wavelength)


        # Determine interpolated wavelength values
        start = np.ceil(wavelength[0])
        end = np.floor(wavelength[len(wavelength)-1])
        new_x = np.arange(start, end, 1)
        #print(new_x)

        newColumns = collections.OrderedDict()
        newColumns["Datetag"] = saveDatetag
        newColumns["Timetag2"] = saveTimetag2
        for i in range(new_x.shape[0]):
            #print(i, new_x[i])
            newColumns[str(new_x[i])] = []

        # Perform interpolation for each row
        for i in range(len(saveDatetag)):
            #print(i)

            values = []
            for k in columns:
                values.append(columns[k][i])
            y = np.asarray(values)
            new_y = interpolate.interp1d(x, y)(new_x)

            for i in range(new_x.shape[0]):
                newColumns[str(new_x[i])].append(new_y[i])


        #newDS = HDFDataset()
        newDS.m_columns = newColumns
        newDS.columnsToDataset()
        #print(ds.m_columns)
        #return newDS


    def getDataAverage(self, n, data, time, width):
        lst = [data[n]]
        i = n-1
        while i >= 0:
            lst.append(data[i])
            if (time[n] - time[i]) > width:
                break
            i -= 1
        i = n+1
        while i < len(time):
            lst.append(data[i])
            if (time[i] - time[n]) > width:
                break
            i += 1
        avg = 0
        for v in lst:
            avg += v
        avg /= len(lst)
        return avg


    def dataAveraging(self, ds):
        
        print("Process Data Average")
        
        interval = 2
        width = 1

        # Copy dataset to dictionary
        columns = collections.OrderedDict()
        for k in [k for k,v in sorted(ds.m_data.dtype.fields.items(), key=lambda k: k[1])]:
            #print("type",type(esData.m_data[k]))
            columns[k] = ds.m_data[k].tolist()
        saveDatetag = columns.pop("Datetag")
        saveTimetag2 = columns.pop("Timetag2")

        # convert timetag2 to seconds
        timer = []
        for i in range(len(saveTimetag2)):
            timer.append(self.timeTag2ToSec(saveTimetag2[i]))

        # new data to return
        newColumns = collections.OrderedDict()
        newColumns["Datetag"] = []
        newColumns["Timetag2"] = []

        i = 0
        v = timer[0]
        while i < len(timer)-1:
            if (timer[i] - v) > interval:
                #print(saveTimetag2[i], timer[i])
                newColumns["Datetag"].append(saveDatetag[i])
                newColumns["Timetag2"].append(saveTimetag2[i])
                v = timer[i]
                i += 2
            else:
                i += 1

        for k in columns:
            data = columns[k]
            newColumns[k] = []

            # generate points to average based on interval
            i = 0            
            v = timer[0]
            while i < len(timer)-1:
                if (timer[i] - v) > interval:
                    avg = self.getDataAverage(i, data, timer, width)
                    newColumns[k].append(avg)
                    v = timer[i]
                    i += 2
                else:
                    i += 1

        ds.m_columns = newColumns
        ds.columnsToDataset()


    def processL3a(self):

        root = HDFRoot()
        root.copyAttributes(self)
        root.m_attributes["PROCESSING_LEVEL"] = "3a"
        root.m_attributes["BIN_INTERVAL"] = "1 m"
        root.m_attributes["BIN_WIDTH"] = "0.5 m"
        root.m_attributes["TIME_INTERVAL"] = "2 sec"
        root.m_attributes["TIME_WIDTH"] = "1 sec"
        root.m_attributes["WAVEL_INTERP"] = "1 nm"

        newReferenceGroup = root.addGroup("Reference")
        newSASGroup = root.addGroup("SAS")
        root.m_groups.append(self.getGroup("GPS"))

        referenceGroup = self.getGroup("Reference")
        sasGroup = self.getGroup("SAS")

        esData = referenceGroup.getDataset("ES_hyperspectral")
        liData = sasGroup.getDataset("LI_hyperspectral")
        ltData = sasGroup.getDataset("LT_hyperspectral")

        newESData = newReferenceGroup.addDataset("ES_hyperspectral")
        newLIData = newSASGroup.addDataset("LI_hyperspectral")
        newLTData = newSASGroup.addDataset("LT_hyperspectral")

        root.interpolateWavelength(esData, newESData)
        root.interpolateWavelength(liData, newLIData)
        root.interpolateWavelength(ltData, newLTData)
    
        root.dataAveraging(newESData)
        root.dataAveraging(newLIData)
        root.dataAveraging(newLTData)

        return root


