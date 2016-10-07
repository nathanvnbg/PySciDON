
import collections

import numpy as np
import scipy as sp

import HDFRoot
#import HDFGroup
#import HDFDataset

from Utilities import Utilities

from config import settings


class ProcessL3a:

    # Interpolates by wavelength
    @staticmethod
    def interpolateWavelength(ds, newDS, interval=1):

        # Copy dataset to dictionary
        ds.datasetToColumns()
        columns = ds.m_columns
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
        new_x = np.arange(start, end, interval)
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
            new_y = sp.interpolate.interp1d(x, y)(new_x)

            for i in range(new_x.shape[0]):
                newColumns[str(new_x[i])].append(new_y[i])


        #newDS = HDFDataset()
        newDS.m_columns = newColumns
        newDS.columnsToDataset()
        #print(ds.m_columns)
        #return newDS


    # Determines points to average data
    # Note: Prosoft always includes 1 point left/right of n
    #       even if it is outside of specified width
    @staticmethod
    def getDataAverage(n, data, time, width):
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

    # Performs averaging on the data
    @staticmethod
    def dataAveraging(ds):
        
        print("Process Data Average")
        
        interval = 2
        width = 1

        # Copy dataset to dictionary
        ds.datasetToColumns()
        columns = ds.m_columns
        saveDatetag = columns.pop("Datetag")
        saveTimetag2 = columns.pop("Timetag2")

        # convert timetag2 to seconds
        timer = []
        for i in range(len(saveTimetag2)):
            timer.append(Utilities.timeTag2ToSec(saveTimetag2[i]))

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

            # Do a natural log transform
            data = np.log(data)

            # generate points to average based on interval
            i = 0            
            v = timer[0]
            while i < len(timer)-1:
                if (timer[i] - v) > interval:
                    avg = ProcessL3a.getDataAverage(i, data, timer, width)
                    newColumns[k].append(avg)
                    v = timer[i]
                    i += 2
                else:
                    i += 1

            newColumns = np.exp(newColumns)

        ds.m_columns = newColumns
        ds.columnsToDataset()

    # Does wavelength interpolation and data averaging
    @staticmethod
    def processL3a(node):

        root = HDFRoot.HDFRoot()
        root.copyAttributes(node)
        root.m_attributes["PROCESSING_LEVEL"] = "3a"
        root.m_attributes["BIN_INTERVAL"] = "1 m"
        root.m_attributes["BIN_WIDTH"] = "0.5 m"
        root.m_attributes["TIME_INTERVAL"] = "2 sec"
        root.m_attributes["TIME_WIDTH"] = "1 sec"
        root.m_attributes["WAVEL_INTERP"] = "1 nm"

        newReferenceGroup = root.addGroup("Reference")
        newSASGroup = root.addGroup("SAS")
        if node.hasGroup("GPS"):
            root.m_groups.append(node.getGroup("GPS"))

        referenceGroup = node.getGroup("Reference")
        sasGroup = node.getGroup("SAS")

        esData = referenceGroup.getDataset("ES_hyperspectral")
        liData = sasGroup.getDataset("LI_hyperspectral")
        ltData = sasGroup.getDataset("LT_hyperspectral")

        newESData = newReferenceGroup.addDataset("ES_hyperspectral")
        newLIData = newSASGroup.addDataset("LI_hyperspectral")
        newLTData = newSASGroup.addDataset("LT_hyperspectral")
        
        interval = int(settings["iL3aInterpInterval"])

        ProcessL3a.interpolateWavelength(esData, newESData, interval)
        ProcessL3a.interpolateWavelength(liData, newLIData, interval)
        ProcessL3a.interpolateWavelength(ltData, newLTData, interval)
    
        #ProcessL3a.dataAveraging(newESData)
        #ProcessL3a.dataAveraging(newLIData)
        #ProcessL3a.dataAveraging(newLTData)

        return root
