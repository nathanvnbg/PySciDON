
import collections
import datetime as dt
import os


import HDFRoot
import HDFGroup
#import HDFDataset

from RawFileReader import RawFileReader


class ProcessL1a:

    # Reads a raw file and generates a L1a HDF file
    @staticmethod
    def processL1a(calibrationMap, fp):
        (dirpath, filename) = os.path.split(fp)

        # Generate root header attributes
        root = HDFRoot.HDFRoot()
        root.m_id = "/"
        root.m_attributes["PROSOFT"] = "Prosoft 9.0.4"
        root.m_attributes["PROSOFT_INSTRUMENT_CONFIG"] = "testcfg"
        root.m_attributes["PROSOFT_PARAMETERS_FILE_NAME"] = "test.mat"
        root.m_attributes["CAL_FILE_NAMES"] = ','.join(calibrationMap.keys())
        root.m_attributes["WAVELENGTH_UNITS"] = "nm"
        root.m_attributes["LU_UNITS"] = "count"
        root.m_attributes["ED_UNITS"] = "count"
        root.m_attributes["ES_UNITS"] = "count"
        root.m_attributes["RAW_FILE_NAME"] = filename

        contextMap = collections.OrderedDict()

        for key in calibrationMap:
            cf = calibrationMap[key]
            gp = HDFGroup.HDFGroup()
            gp.m_id = cf.m_instrumentType
            contextMap[cf.m_id] = gp

        #print("contextMap:", list(contextMap.keys()))

        RawFileReader.readRawFile(fp, calibrationMap, contextMap, root)

        # Generates group attributes
        for key in calibrationMap:
            cf = calibrationMap[key]
            gp = contextMap[cf.m_id]
            gp.m_attributes["InstrumentType"] = cf.m_instrumentType
            gp.m_attributes["Media"] = cf.m_media
            gp.m_attributes["MeasMode"] = cf.m_measMode
            gp.m_attributes["FrameType"] = cf.m_frameType
            gp.m_attributes["INSTRUMENT_NO"] = "1"
            gp.getTableHeader(cf.m_sensorType)
            gp.m_attributes["DISTANCE_1"] = "Pressure " + cf.m_sensorType + " 1 1 0"
            gp.m_attributes["DISTANCE_2"] = "Surface " + cf.m_sensorType + " 1 1 0"
            gp.m_attributes["SensorDataList"] = ", ".join([x for x in gp.m_datasets.keys()])
            root.m_groups.append(gp)


        # Generates root footer attributes
        root.m_attributes["PROCESSING_LEVEL"] = "1a"
        now = dt.datetime.now()
        timestr = now.strftime("%d-%b-%Y %H:%M:%S")
        root.m_attributes["FILE_CREATION_TIME"] = timestr

        # Converts gp.m_columns to numpy array
        for gp in root.m_groups:
            for ds in gp.m_datasets.values():
                ds.columnsToDataset()
        #RawFileReader.generateContext(root)

        return root
