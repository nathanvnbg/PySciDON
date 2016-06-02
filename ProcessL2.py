
import collections

import numpy as np


import HDFRoot
#import HDFGroup
#import HDFDataset

from Utilities import Utilities


class ProcessL2:

    # ToDo: improve later
    # Reference: "ProSoft-7.7- Manual.pdf", Appendix D
    @staticmethod
    def dataDeglitching(ds):
        noiseThresh = 20        

        # Copy dataset to dictionary
        ds.datasetToColumns()
        columns = ds.m_columns

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

        #ds.m_columns = columns
        ds.columnsToDataset()

    @staticmethod
    def processDataDeglitching(node, sensorType):
        darkData = None
        for gp in node.m_groups:
            if gp.m_attributes["FrameType"] == "ShutterDark" and gp.hasDataset(sensorType):
                darkData = gp.getDataset(sensorType)
      
        ProcessL2.dataDeglitching(darkData)



    @staticmethod
    def darkCorrection(darkData, darkTimer, lightData, lightTimer):
        if (darkData == None) or (lightData == None):
            print("Dark Correction, dataset not found:", darkData, lightData)
            return

        '''
        #print("test", lightData.m_id)
        # Prosoft - Replace Light Timer with closest value in Dark Timer, interpolate Light Data
        oldLightTimer = np.copy(lightTimer.m_data["NONE"]).tolist()
        j = 0
        for i in range(len(darkTimer.m_data["NONE"])):
            v = darkTimer.m_data["NONE"][i]
            closest = [0, abs(lightTimer.m_data["NONE"][0] - v)]
            for j in range(1, len(lightTimer.m_data["NONE"])):
                if abs(lightTimer.m_data["NONE"][j] - v) < closest[1]:
                    closest[0] = j
                    closest[1] = abs(lightTimer.m_data["NONE"][j] - v)
            if closest[0] != len(lightTimer.m_data["NONE"])-1:
                #print(closest)
                lightTimer.m_data["NONE"][closest[0]] = v

        newLightData = np.copy(lightData.m_data)
        for k in darkData.m_data.dtype.fields.keys():
            x = np.copy(oldLightTimer).tolist()
            y = np.copy(lightData.m_data[k]).tolist()
            #print("t1", len(x), len(y))
            #print(len(x),len(y))
            new_x = lightTimer.m_data["NONE"]
            #newLightData[k] = Utilities.interp(x,y,new_x,'linear')
            newLightData[k] = Utilities.interp(x,y,new_x,'cubic')
        lightData.m_data = newLightData
        '''

        # Interpolate Dark Dataset to match number of elements as Light Dataset
        newDarkData = np.copy(lightData.m_data)
        for k in darkData.m_data.dtype.fields.keys():
            x = np.copy(darkTimer.m_data["NONE"]).tolist()
            y = np.copy(darkData.m_data[k]).tolist()
            new_x = lightTimer.m_data["NONE"]
            #newDarkData[k] = Utilities.interp(x,y,new_x,'linear')
            newDarkData[k] = Utilities.interp(x,y,new_x,'cubic')
        darkData.m_data = newDarkData

        #print(lightData.m_data.shape)
        #print(newDarkData.shape)

        # Correct light data by subtracting interpolated dark data from light data
        for k in lightData.m_data.dtype.fields.keys():
            for x in range(lightData.m_data.shape[0]):
                lightData.m_data[k][x] -= newDarkData[k][x]

        #print(lightData.m_data)

    # Code to recalculate light/dark timer values to start near zero
    # Might work better when preforming interpolations?
    @staticmethod
    def processTimer(darkTimer, lightTimer):

        if (darkTimer.m_data is not None) and (lightTimer.m_data is not None):
            t0 = lightTimer.m_data["NONE"][0]
            t1 = lightTimer.m_data["NONE"][1]
            #offset = t1 - t0

            # Finds the minimum cycle time of the instrument to use as offset
            min0 = t1 - t0
            total = len(lightTimer.m_data["NONE"])
            #print("test avg")
            for i in range(1, total):
                num = lightTimer.m_data["NONE"][i] - lightTimer.m_data["NONE"][i-1]
                if num < min0:
                    min0 = num
            offset = min0
            #print("min:",min0)

            # Set start time to minimum of light/dark timer values
            if darkTimer.m_data["NONE"][0] < t0:
                t0 = darkTimer.m_data["NONE"][0]

            # Recalculate timers by subtracting start time and adding offset
            #print("Time:", time)
            #print(darkTimer.m_data)
            for i in range(0, len(darkTimer.m_data)):
                darkTimer.m_data["NONE"][i] += -t0 + offset
            for i in range(0, len(lightTimer.m_data)):
                lightTimer.m_data["NONE"][i] += -t0 + offset
            #print(darkTimer.m_data)


    @staticmethod
    def processDarkCorrection(node, sensorType):
        darkData = None
        darkTimer = None
        lightData = None
        lightTimer = None

        for gp in node.m_groups:
            if gp.m_attributes["FrameType"] == "ShutterDark" and gp.hasDataset(sensorType):
                darkData = gp.getDataset(sensorType)
                darkTimer = gp.getDataset("TIMER")

            if gp.m_attributes["FrameType"] == "ShutterLight" and gp.hasDataset(sensorType):
                lightData = gp.getDataset(sensorType)
                lightTimer = gp.getDataset("TIMER")

        ProcessL2.processTimer(darkTimer, lightTimer)
        ProcessL2.darkCorrection(darkData, darkTimer, lightData, lightTimer)



    # Applies dark data correction / data deglitching
    @staticmethod
    def processL2(node):
        root = HDFRoot.HDFRoot()
        root.copy(node)

        root.m_attributes["PROCESSING_LEVEL"] = "2"
        root.m_attributes["DEGLITCH_PRODAT"] = "OFF"
        root.m_attributes["DEGLITCH_REFDAT"] = "OFF"
        #root.m_attributes["STRAY_LIGHT_CORRECT"] = "OFF"
        #root.m_attributes["THERMAL_RESPONSIVITY_CORRECT"] = "OFF"

        # Recalculate TIMER dataset, it is used for interpolating dark data
        #print("Start Time:", root.getStartTime())
        #root.processTIMER()
        #root.processTIMERProsoft()

        #ProcessL2.processDataDeglitching(root, "ES")
        #ProcessL2.processDataDeglitching(root, "LI")
        #ProcessL2.processDataDeglitching(root, "LT")

        ProcessL2.processDarkCorrection(root, "ES")
        ProcessL2.processDarkCorrection(root, "LI")
        ProcessL2.processDarkCorrection(root, "LT")

        return root
