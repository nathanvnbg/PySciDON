
import collections

import numpy as np
import scipy as sp

import HDFRoot
#import HDFGroup
#import HDFDataset

from Utilities import Utilities


class ProcessL4:
    
    @staticmethod
    def qualityCheck(es5Columns):

        # Threshold for significant es
        v = es5Columns["480.0"][0]        
        if v < 2:
            print("Quality Check: ES(480.0) =", v)
            return False

        # Masking spectra affected by dawn/dusk radiation
        v = es5Columns["470.0"][0] / es5Columns["610.0"][0]
        if v < 1:
            print("Quality Check: ES(470.0)/ES(610.0) =", v)
            return False

        # Masking spectra affected by rainfall and high humidity
        v = es5Columns["720.0"][0] / es5Columns["370.0"][0]        
        if v < 1.2:
            print("Quality Check: ES(720.0)/ES(370.0) =", v)
            return False

        return True


    @staticmethod
    def calculateReflectance(esData, liData, ltData, newRrsData):

        # Copy datasets to dictionary
        esData.datasetToColumns()
        esColumns = esData.m_columns
        esColumns.pop("Datetag")
        esColumns.pop("Timetag2")

        liData.datasetToColumns()
        liColumns = liData.m_columns
        liColumns.pop("Datetag")
        liColumns.pop("Timetag2")

        ltData.datasetToColumns()
        ltColumns = ltData.m_columns
        ltColumns.pop("Datetag")
        ltColumns.pop("Timetag2")

        if Utilities.detectNan(esData):
            print("Found NAN 1") 
            exit

        if Utilities.detectNan(liData):
            print("Found NAN 2") 
            exit

        if Utilities.detectNan(ltData):
            print("Found NAN 3") 
            exit


        esLength = len(list(esColumns.items())[0])
        ltLength = len(list(ltColumns.items())[0])

        if ltLength > esLength:
            for col in ltColumns:
                col = col[0:esLength]
            for col in liColumns:
                col = col[0:esLength]


        # Import wind data - ToDo

        # Calculates the lowest 5% (based on Hooker & Morel 2003)
        n = len(list(ltColumns.items())[0])
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


        # Exit if detect nan
        if hasNan:
            print("Error NaN Found")
            return False

        #if not ProcessL4.qualityCheck(es5Columns):
        #    return False


        # Calculate Rho_sky
        sky750 = li5Columns["751.0"][0]/es5Columns["751.0"][0]

        # ToDo: sunny/wind calculations
        p_sky = 0.0256


        # Calculate Rrs
        rrsColumns = collections.OrderedDict()
        for k in es5Columns:
            if (k in li5Columns) and (k in lt5Columns):
                es = es5Columns[k][0]
                li = li5Columns[k][0]
                lt = lt5Columns[k][0]
                rrsColumns[k] = [(lt - (p_sky * li)) / es]

        newRrsData.m_columns = rrsColumns
        newRrsData.columnsToDataset()

        return True


    # Does wavelength interpolation and data averaging
    @staticmethod
    def processL4(node):

        root = HDFRoot.HDFRoot()
        root.copyAttributes(node)
        root.m_attributes["PROCESSING_LEVEL"] = "4"

        newReflectanceGroup = root.addGroup("Reflectance")

        referenceGroup = node.getGroup("Reference")
        sasGroup = node.getGroup("SAS")

        esData = referenceGroup.getDataset("ES_hyperspectral")
        liData = sasGroup.getDataset("LI_hyperspectral")
        ltData = sasGroup.getDataset("LT_hyperspectral")

        newRrsData = newReflectanceGroup.addDataset("Rrs")

        if not ProcessL4.calculateReflectance(esData, liData, ltData, newRrsData):
            return None

        return root
