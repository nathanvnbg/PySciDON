
import numpy as np

import HDFRoot
#import HDFGroup
#import HDFDataset

from Utilities import Utilities


class ProcessL2s:

    # recalculate TimeTag2 to follow GPS UTC time
    @staticmethod
    def processGPSTime(node):
        sec = 0

        for gp in node.m_groups:
            #if gp.m_id.startswith("GPS"):
            if gp.hasDataset("UTCPOS"):
                ds = gp.getDataset("UTCPOS")
                sec = Utilities.utcToSec(ds.m_data["NONE"][0])
                #print("GPS UTCPOS:", ds.m_data["NONE"][0], "-> sec:", sec)
                #print(secToUtc(sec))

        for gp in node.m_groups:
            #if not gp.m_id.startswith("GPS"):
            if not gp.hasDataset("UTCPOS"):
                dsTimer = gp.getDataset("TIMER")
                dsTimeTag2 = gp.getDataset("TIMETAG2")
                for x in range(dsTimeTag2.m_data.shape[0]):
                    v = dsTimer.m_data["NONE"][x] + sec
                    dsTimeTag2.m_data["NONE"][x] = Utilities.secToTimeTag2(v)


    @staticmethod
    def interpolateL2s(xData, xTimer, yTimer, newXData, kind='linear'):
        for k in [k for k,v in sorted(xData.m_data.dtype.fields.items(),key=lambda k: k[1])]:
            x = list(xTimer)
            new_x = list(yTimer)
            y = np.copy(xData.m_data[k]).tolist()
            newXData.m_columns[k] = Utilities.interp(x, y, new_x, kind)

    # interpolate GPS to match ES using linear interpolation
    @staticmethod
    def interpolateGPSData(node, esGroup, gpsGroup):
        print("Interpolate GPS Data2")

        # ES
        # Generates ES_hyperspectral dataset with appended Datetag/Timetag2 columns
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
        # Creates new gps group with Datetag/Timetag2 columns appended to all datasets
        gpsTimeData = gpsGroup.getDataset("UTCPOS")
        gpsCourseData = gpsGroup.getDataset("COURSE")
        gpsLatPosData = gpsGroup.getDataset("LATPOS")
        gpsLonPosData = gpsGroup.getDataset("LONPOS")
        gpsMagVarData = gpsGroup.getDataset("MAGVAR")
        gpsSpeedData = gpsGroup.getDataset("SPEED")

        newGPSGroup = node.getGroup("GPS")
        newGPSCourseData = newGPSGroup.addDataset("COURSE")
        newGPSLatPosData = newGPSGroup.addDataset("LATPOS")
        newGPSLonPosData = newGPSGroup.addDataset("LONPOS")
        newGPSMagVarData = newGPSGroup.addDataset("MAGVAR")
        newGPSSpeedData = newGPSGroup.addDataset("SPEED")

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


        # Convert GPS UTC time values to seconds to be used for interpolation
        xTimer = []
        for i in range(gpsTimeData.m_data.shape[0]):
            xTimer.append(Utilities.utcToSec(gpsTimeData.m_data["NONE"][i]))

        # Convert ES TimeTag2 values to seconds to be used for interpolation
        yTimer = []
        for i in range(esTimeData.m_data.shape[0]):
            yTimer.append(Utilities.timeTag2ToSec(esTimeData.m_data["NONE"][i]))


        # Interpolate by time values
        ProcessL2s.interpolateL2s(gpsCourseData, xTimer, yTimer, newGPSCourseData, 'linear')
        ProcessL2s.interpolateL2s(gpsLatPosData, xTimer, yTimer, newGPSLatPosData, 'linear')
        ProcessL2s.interpolateL2s(gpsLonPosData, xTimer, yTimer, newGPSLonPosData, 'linear')
        ProcessL2s.interpolateL2s(gpsMagVarData, xTimer, yTimer, newGPSMagVarData, 'linear')
        ProcessL2s.interpolateL2s(gpsSpeedData, xTimer, yTimer, newGPSSpeedData, 'linear')


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
    @staticmethod
    def interpolateSASData(node, liGroup, ltGroup):
        print("Interpolate SAS Data2")

        # Generates LT_hyperspectral/LI_hyperspectral datasets
        # with appended Datetag/Timetag2 columns

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


        # Convert LT/LI TimeTag2 values to seconds to be used for interpolation
        xTimer = []
        for i in range(ltTimeData.m_data.shape[0]):
            xTimer.append(Utilities.timeTag2ToSec(ltTimeData.m_data["NONE"][i]))
        yTimer = []
        for i in range(liTimeData.m_data.shape[0]):
            yTimer.append(Utilities.timeTag2ToSec(liTimeData.m_data["NONE"][i]))


        # interpolate
        ProcessL2s.interpolateL2s(ltData, xTimer, yTimer, newLTData, 'cubic')

        newLTData.columnsToDataset()


    # Interpolates datasets so they have common time coordinates
    @staticmethod
    def processL2s(node):

        ProcessL2s.processGPSTime(node)

        root = HDFRoot.HDFRoot()
        root.copyAttributes(node)
        root.m_attributes["PROCESSING_LEVEL"] = "2s"
        root.m_attributes["DEPTH_RESOLUTION"] = "0.1 m"

        root.addGroup("GPS")
        root.addGroup("Reference")
        root.addGroup("SAS")
        
        esGroup = None
        gpsGroup = None
        liGroup = None
        ltGroup = None
        for gp in node.m_groups:
            #if gp.m_id.startswith("GPS"):
            if gp.hasDataset("UTCPOS"):
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

        ProcessL2s.interpolateGPSData(root, esGroup, gpsGroup)
        ProcessL2s.interpolateSASData(root, liGroup, ltGroup)
    
        return root
