
import collections
import sys

import numpy as np
import scipy as sp

import HDFRoot
#import HDFGroup
#import HDFDataset

from Utilities import Utilities
from WindSpeedReader import WindSpeedReader

from config import settings


class ProcessL4:


    # Perform meteorological flag checking
    @staticmethod
    def qualityCheckVar(es5Columns, esFlag, dawnDuskFlag, humidityFlag):

        # Threshold for significant es
        v = es5Columns["480.0"][0]        
        if v < esFlag:
            print("Quality Check: ES(480.0) =", v)
            return False

        # Masking spectra affected by dawn/dusk radiation
        v = es5Columns["470.0"][0] / es5Columns["610.0"][0] # Fix 610 -> 680
        if v < dawnDuskFlag:
            print("Quality Check: ES(470.0)/ES(610.0) =", v)
            return False

        # Masking spectra affected by rainfall and high humidity
        v = es5Columns["720.0"][0] / es5Columns["370.0"][0]        
        if v < humidityFlag:
            print("Quality Check: ES(720.0)/ES(370.0) =", v)
            return False

        return True

    # Perform meteorological flag checking with settings from config
    @staticmethod
    def qualityCheck(es5Columns):
        esFlag = float(settings["fL4SignificantEsFlag"])
        dawnDuskFlag = float(settings["fL4DawnDuskFlag"])
        humidityFlag = float(settings["fL4RainfallHumidityFlag"])

        result = ProcessL4.qualityCheckVar(es5Columns, esFlag, dawnDuskFlag, humidityFlag)

        return result


    # Take a slice of a dataset stored in columns
    @staticmethod
    def columnToSlice(columns, start, end):
        newSlice = collections.OrderedDict()
        for k in columns:
            newSlice[k] = columns[k][start:end]
        return newSlice


    @staticmethod
    def calculateReflectance2(root, esColumns, liColumns, ltColumns, newRrsData, newESData, newLIData, newLTData, enableQualityCheck, defaultWindSpeed=0.0, windSpeedColumns=None):

        # Calculates the lowest 5% (based on Hooker & Morel 2003)
        n = len(list(ltColumns.values())[0])
        x = round(n*5/100)
        if n <= 5:
            x = n


        #print(ltColumns["780.0"])

        # Find the indexes for the lowest 5%
        lt780 = ltColumns["780.0"]
        index = np.argsort(lt780)
        y = index[0:x]


        # Takes the mean of the lowest 5%
        es5Columns = collections.OrderedDict()
        li5Columns = collections.OrderedDict()
        lt5Columns = collections.OrderedDict()
        windSpeedMean = defaultWindSpeed


        # Checks if the data has NaNs
        hasNan = False
        for k in esColumns:
            v = [esColumns[k][i] for i in y]
            mean = np.nanmean(v)
            es5Columns[k] = [mean]
            if np.isnan(mean):
                hasNan = True
        for k in liColumns:
            v = [liColumns[k][i] for i in y]
            mean = np.nanmean(v)
            li5Columns[k] = [mean]
            if np.isnan(mean):
                hasNan = True
        for k in ltColumns:
            v = [ltColumns[k][i] for i in y]
            mean = np.nanmean(v)
            lt5Columns[k] = [mean]
            if np.isnan(mean):
                hasNan = True

        # Mean of wind speed for data
        if windSpeedColumns is not None:
            v = [windSpeedColumns[i] for i in y]
            mean = np.nanmean(v)
            windSpeedMean = mean
            if np.isnan(mean):
                hasNan = True


        # Exit if detect NaN
        if hasNan:
            print("Error NaN Found")
            return False

        # Test meteorological flags
        if enableQualityCheck:
            if not ProcessL4.qualityCheck(es5Columns):
                return False


        # Calculate Rho_sky
        sky750 = li5Columns["750.0"][0]/es5Columns["750.0"][0]

        # ToDo: sunny/wind calculations
        if sky750 > 0.05:
            p_sky = 0.0256
        else:
            # Set wind speed here
            w = windSpeedMean
            p_sky = 0.0256 + 0.00039 * w + 0.000034 * w * w
            #p_sky = 0.0256


        # Calculate Rrs
        for k in es5Columns:
            if (k in li5Columns) and (k in lt5Columns):
                if k not in newESData.m_columns:
                    newESData.m_columns[k] = []
                    newLIData.m_columns[k] = []
                    newLTData.m_columns[k] = []
                    newRrsData.m_columns[k] = []
                #print(len(newESData.m_columns[k]))
                es = es5Columns[k][0]
                li = li5Columns[k][0]
                lt = lt5Columns[k][0]
                rrs = (lt - (p_sky * li)) / es
                #esColumns[k] = [es]
                #liColumns[k] = [li]
                #ltColumns[k] = [lt]
                #rrsColumns[k] = [(lt - (p_sky * li)) / es]
                newESData.m_columns[k].append(es)
                newLIData.m_columns[k].append(li)
                newLTData.m_columns[k].append(lt)
                newRrsData.m_columns[k].append(rrs)

        return True



    @staticmethod
    def calculateReflectance(root, node, interval, enableQualityCheck, defaultWindSpeed=0.0, windSpeedData=None):
    #def calculateReflectance(esData, liData, ltData, newRrsData, newESData, newLIData, newLTData):


        referenceGroup = node.getGroup("Reference")
        sasGroup = node.getGroup("SAS")

        esData = referenceGroup.getDataset("ES_hyperspectral")
        liData = sasGroup.getDataset("LI_hyperspectral")
        ltData = sasGroup.getDataset("LT_hyperspectral")


        newReflectanceGroup = root.getGroup("Reflectance")
        newRrsData = newReflectanceGroup.addDataset("Rrs")
        newESData = newReflectanceGroup.addDataset("ES")
        newLIData = newReflectanceGroup.addDataset("LI")
        newLTData = newReflectanceGroup.addDataset("LT")


        # Copy datasets to dictionary
        esData.datasetToColumns()
        esColumns = esData.m_columns
        esColumns.pop("Datetag")
        tt2 = esColumns.pop("Timetag2")

        liData.datasetToColumns()
        liColumns = liData.m_columns
        liColumns.pop("Datetag")
        liColumns.pop("Timetag2")

        ltData.datasetToColumns()
        ltColumns = ltData.m_columns
        ltColumns.pop("Datetag")
        ltColumns.pop("Timetag2")

        # remove added LATPOS/LONPOS if added
        if "LATPOS" in esColumns:
            esColumns.pop("LATPOS")
            liColumns.pop("LATPOS")
            ltColumns.pop("LATPOS")
        if "LONPOS" in esColumns:
            esColumns.pop("LONPOS")
            liColumns.pop("LONPOS")
            ltColumns.pop("LONPOS")


        if Utilities.hasNan(esData):
            print("Found NAN 1") 
            sys.exit(1)

        if Utilities.hasNan(liData):
            print("Found NAN 2") 
            sys.exit(1)

        if Utilities.hasNan(ltData):
            print("Found NAN 3") 
            sys.exit(1)

        esLength = len(list(esColumns.values())[0])
        ltLength = len(list(ltColumns.values())[0])

        if ltLength > esLength:
            for col in ltColumns:
                col = col[0:esLength]
            for col in liColumns:
                col = col[0:esLength]

        windSpeedColumns=None

        # interpolate wind speed to match sensor time values
        if windSpeedData is not None:
            x = windSpeedData.getColumn("TIMETAG2")[0]
            y = windSpeedData.getColumn("WINDSPEED")[0]
            new_x = esData.m_data["Timetag2"].tolist()
            new_y = Utilities.interp(x, y, new_x)
            windSpeedData.m_columns["WINDSPEED"] = new_y
            windSpeedData.m_columns["TIMETAG2"] = new_x
            windSpeedData.columnsToDataset()
            windSpeedColumns = new_y

        #print("items:", esColumns.values())
        #print(ltLength,resolution)
        start = 0
        #end = 0
        endTime = Utilities.timeTag2ToSec(tt2[0]) + interval
        for i in range(0, len(tt2)):
            time = Utilities.timeTag2ToSec(tt2[i])
            if time > endTime:
                end = i-1
                esSlice = ProcessL4.columnToSlice(esColumns, start, end)
                liSlice = ProcessL4.columnToSlice(liColumns, start, end)
                ltSlice = ProcessL4.columnToSlice(ltColumns, start, end)
                ProcessL4.calculateReflectance2(root, esSlice, liSlice, ltSlice, newRrsData, newESData, newLIData, newLTData, enableQualityCheck, defaultWindSpeed, windSpeedColumns)
                
                start = i
                endTime = time + interval


#        for i in range(0, int(esLength/resolution)):
#            #print(i)
#            start = i*resolution
#            end = start+resolution
#            esSlice = ProcessL4.columnToSlice(esColumns, start, end, i, resolution)
#            liSlice = ProcessL4.columnToSlice(liColumns, start, end, i, resolution)
#            ltSlice = ProcessL4.columnToSlice(ltColumns, start, end, i, resolution)
#
#            ProcessL4.calculateReflectance2(root, esSlice, liSlice, ltSlice, newRrsData, newESData, newLIData, newLTData, enableQualityCheck, defaultWindSpeed, windSpeedColumns)


        newESData.columnsToDataset()
        newLIData.columnsToDataset()
        newLTData.columnsToDataset()
        newRrsData.columnsToDataset()


        return True


    # Does wavelength interpolation and data averaging
    @staticmethod
    def processL4(node, windSpeedData=None):

        root = HDFRoot.HDFRoot()
        root.copyAttributes(node)
        root.m_attributes["PROCESSING_LEVEL"] = "4"

        root.addGroup("Reflectance")

        interval = float(settings["fL4TimeInterval"])
        enableQualityCheck = int(settings["bEnableQualityFlags"])
        defaultWindSpeed = float(settings["fDefaultWindSpeed"])
        #windDirectory = settings["sWindSpeedFolder"].strip('"')

        # Can change time resolution here
        if not ProcessL4.calculateReflectance(root, node, interval, enableQualityCheck, defaultWindSpeed, windSpeedData):
            return None

        return root
