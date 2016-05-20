
import HDFRoot
#import HDFGroup
#import HDFDataset

class ProcessL1b:

    # Calibrates raw data from L1a using information from calibration file
    @staticmethod
    def processL1b(node, calibrationMap): # ToDo: Switch to contextMap
        root = HDFRoot.HDFRoot()
        root.copy(node)

        root.m_attributes["PROCESSING_LEVEL"] = "1b"

        esUnits = None
        luUnits = None

        for gp in root.m_groups:
            #cf = calibrationMap[gp.m_attributes["FrameTag"]]
            cf = calibrationMap[gp.m_attributes["CalFileName"]]
            #print(gp.m_id, gp.m_attributes)
            print("File:", cf.m_id)
            gp.processCalibration(cf)

            if esUnits == None:
                esUnits = cf.getUnits("ES")
            if luUnits == None:
                luUnits = cf.getUnits("LI")

        #print(esUnits, luUnits)
        root.m_attributes["LU_UNITS"] = luUnits
        root.m_attributes["ED_UNITS"] = esUnits
        root.m_attributes["ES_UNITS"] = esUnits

        return root
