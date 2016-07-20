
import HDFRoot
#import HDFGroup
#import HDFDataset

class ProcessL1b:



    # Used to calibrate raw data (convert from L1a to L1b)
    # Reference: "SAT-DN-00134_Instrument File Format.pdf"
    @staticmethod
    def processDataset(ds, cd, inttime=None, immersed=False):
        #print("FitType:", cd.m_fitType)
        if cd.m_fitType == "OPTIC1":
            ProcessL1b.processOPTIC1(ds, cd, immersed)
        elif cd.m_fitType == "OPTIC2":
            ProcessL1b.processOPTIC2(ds, cd, immersed)
        elif cd.m_fitType == "OPTIC3":
            ProcessL1b.processOPTIC3(ds, cd, immersed, inttime)
        elif cd.m_fitType == "OPTIC4":
            ProcessL1b.processOPTIC4(ds, cd, immersed)
        elif cd.m_fitType == "THERM1":
            ProcessL1b.processTHERM1(ds, cd)
        elif cd.m_fitType == "POW10":
            ProcessL1b.processPOW10(ds, cd, immersed)
        elif cd.m_fitType == "POLYU":
            ProcessL1b.processPOLYU(ds, cd)
        elif cd.m_fitType == "POLYF":
            ProcessL1b.processPOLYF(ds, cd)
        elif cd.m_fitType == "DDMM":
            ProcessL1b.processDDMM(ds, cd)
        elif cd.m_fitType == "HHMMSS":
            ProcessL1b.processHHMMSS(ds, cd)
        elif cd.m_fitType == "DDMMYY":
            ProcessL1b.processDDMMYY(ds, cd)
        elif cd.m_fitType == "TIME2":
            ProcessL1b.processTIME2(ds, cd)
        elif cd.m_fitType == "COUNT":
            pass
        elif cd.m_fitType == "NONE":
            pass
        else:
            print("Unknown Fit Type:", cd.m_fitType)

    # Process OPTIC1 - not implemented
    @staticmethod
    def processOPTIC1(ds, cd, immersed):
        return

    @staticmethod
    def processOPTIC2(ds, cd, immersed):
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        k = cd.m_id
        for x in range(ds.m_data.shape[0]):
            ds.m_data[k][x] = im * a1 * (ds.m_data[k][x] - a0)

    @staticmethod
    def processOPTIC3(ds, cd, immersed, inttime):
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        cint = float(cd.m_coefficients[3])
        #print(inttime.m_data.shape[0], self.m_data.shape[0])
        k = cd.m_id
        #print(cint, aint)
        #print(cd.m_id)
        for x in range(ds.m_data.shape[0]):
            aint = inttime.m_data[cd.m_type][x]
            #v = self.m_data[k][x]
            ds.m_data[k][x] = im * a1 * (ds.m_data[k][x] - a0) * (cint/aint)

    @staticmethod
    def processOPTIC4(ds, cd, immersed):
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        cint = float(cd.m_coefficients[3])
        k = cd.m_id
        aint = 1
        for x in range(ds.m_data.shape[0]):
            ds.m_data[k][x] = im * a1 * (ds.m_data[k][x] - a0) * (cint/aint)

    # Process THERM1 - not implemented
    @staticmethod
    def processTHERM1(ds, cd):
        return

    @staticmethod
    def processPOW10(ds, cd, immersed):
        a0 = float(cd.m_coefficients[0])
        a1 = float(cd.m_coefficients[1])
        im = float(cd.m_coefficients[2]) if immersed else 1.0
        k = cd.m_id
        for x in range(ds.m_data.shape[0]):
            ds.m_data[k][x] = im * pow(10, ((ds.m_data[k][x]-a0)/a1))

    @staticmethod
    def processPOLYU(ds, cd):
        k = cd.m_id
        for x in range(ds.m_data.shape[0]):
            num = 0
            for i in range(0, len(cd.m_coefficients)):
                a = float(cd.m_coefficients[i])
                num += a * pow(ds.m_data[k][x],i)
            ds.m_data[k][x] = num

    @staticmethod
    def processPOLYF(ds, cd):
        a0 = float(cd.m_coefficients[0])
        k = cd.m_id
        for x in range(ds.m_data.shape[0]):
            num = a0
            for a in cd.m_coefficients[1:]:
                num *= (ds.m_data[k][x] - float(a))
            ds.m_data[k][x] = num

    # Process DDMM - not implemented
    @staticmethod
    def processDDMM(ds, cd):
        return
        #s = "{:.2f}".format(x)
        #x = s[:1] + " " + s[1:3] + "\' " + s[3:5] + "\""

    # Process HHMMSS - not implemented
    @staticmethod
    def processHHMMSS(ds, cd):
        return
        #s = "{:.2f}".format(x)
        #x = s[:2] + ":" + s[2:4] + ":" + s[4:6] + "." + s[6:8]

    # Process DDMMYY - not implemented
    @staticmethod
    def processDDMMYY(ds, cd):
        return
        #s = str(x)
        #x = s[:2] + "/" + s[2:4] + "/" + s[4:]

    # Process TIME2 - not implemented
    @staticmethod
    def processTIME2(ds, cd):
        return
        #x = datetime.fromtimestamp(x).strftime("%y-%m-%d %H:%M:%S")



    # Used to calibrate raw data (from L1a to L1b)
    @staticmethod
    def processGroup(gp, cf):
        inttime = None
        for cd in cf.m_data:
            if cd.m_type == "INTTIME":
                #print("Process INTTIME")
                ds = gp.getDataset("INTTIME")
                ProcessL1b.processDataset(ds, cd)
                inttime = ds

        for cd in cf.m_data:
            if gp.hasDataset(cd.m_type) and cd.m_type != "INTTIME":
                #print("Dataset:", cd.m_type)
                ds = gp.getDataset(cd.m_type)
                ProcessL1b.processDataset(ds, cd, inttime)




    # Calibrates raw data from L1a using information from calibration file
    @staticmethod
    def processL1b(node, calibrationMap): # ToDo: Switch to contextMap
        root = HDFRoot.HDFRoot()
        root.copy(node)

        root.m_attributes["PROCESSING_LEVEL"] = "1b"

        esUnits = None
        luUnits = None

        for gp in root.m_groups:
            #print("Group: ", gp.m_id)
            if "CalFileName" in gp.m_attributes:
                #cf = calibrationMap[gp.m_attributes["FrameTag"]]
                cf = calibrationMap[gp.m_attributes["CalFileName"]]
                #print(gp.m_id, gp.m_attributes)
                print("File:", cf.m_id)
                ProcessL1b.processGroup(gp, cf)
    
                if esUnits == None:
                    esUnits = cf.getUnits("ES")
                if luUnits == None:
                    luUnits = cf.getUnits("LI")

        #print(esUnits, luUnits)
        root.m_attributes["LU_UNITS"] = luUnits
        root.m_attributes["ED_UNITS"] = esUnits
        root.m_attributes["ES_UNITS"] = esUnits

        return root
