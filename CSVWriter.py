
import csv
import os

import numpy as np

from HDFRoot import HDFRoot


class CSVWriter:
    
    @staticmethod
    def formatData(ds, dsTimer):
        dataOut = []
        #columnName = dsName.lower()

        total = ds.m_data.shape[0]
        #ls = ["wl"] + [k for k,v in sorted(ds.m_data.dtype.fields.items(), key=lambda k: k[1])]
        ls = [""] + list(ds.m_data.dtype.names)
        dataOut.append(ls)
        for i in range(total):
            #n = str(i+1)
            #ls = [columnName + "_" + name + '_' + n] + ['%f' % num for num in ds.m_data[i]]
            #print(dsTimer.m_data["NONE"][i])
            ls = [dsTimer.m_data["NONE"][i]] + ['%f' % num for num in ds.m_data[i]]
            dataOut.append(ls)

        return dataOut


    @staticmethod
    def formatData2(data, timer):
        dataOut = []
        #columnName = dsName.lower()

        total = data.shape[0]
        #ls = ["wl"] + [k for k,v in sorted(ds.m_data.dtype.fields.items(), key=lambda k: k[1])]
        ls = [""] + list(data.dtype.names)
        dataOut.append(ls)
        for i in range(total):
            #n = str(i+1)
            #ls = [columnName + "_" + name + '_' + n] + ['%f' % num for num in ds.m_data[i]]
            #print(dsTimer.m_data["NONE"][i])
            ls = [timer[i]] + ['%f' % num for num in data[i]]
            dataOut.append(ls)

        return dataOut


    @staticmethod
    def writeCSV(name, dirpath, data, sensorName, level):
        filename = name + "_" + sensorName + "_" + level
        csvPath = os.path.join(dirpath, filename + ".csv")
        #np.savetxt(csvPath, data, delimiter=',')
        with open(csvPath, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(data)


    @staticmethod
    def outputTXT_L1a(fp):
        CSVWriter.outputTXT_Type1(fp, "L1a")

    @staticmethod
    def outputTXT_L1b(fp):
        CSVWriter.outputTXT_Type1(fp, "L1b")

    @staticmethod
    def outputTXT_L2(fp):
        CSVWriter.outputTXT_Type1(fp, "L2")


    @staticmethod
    def outputTXT_Type1(fp, level):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]

        filepath = os.path.join(dirpath, filename + "_" + level + ".hdf")
        if not os.path.isfile(filepath):
            return

        root = HDFRoot.readHDF5(filepath)
        if root is None:
            print("outputCSV: root is None")
            return

        dirpath = "csv"
        #name = filename[28:43]
        name = filename[0:15]
        esData = None
        liData = None
        ltData = None

        for gp in root.m_groups:
            if gp.m_attributes["FrameType"] == "ShutterLight":
                if gp.hasDataset("ES"):
                    esData = gp.getDataset("ES")
                    esTimer = gp.getDataset("TIMETAG2")
                elif gp.hasDataset("LI"):
                    liData = gp.getDataset("LI")
                    liTimer = gp.getDataset("TIMETAG2")
                elif gp.hasDataset("LT"):
                    ltData = gp.getDataset("LT")
                    ltTimer = gp.getDataset("TIMETAG2")

        if esData is not None and liData is not None and ltData is not None:
            es = CSVWriter.formatData(esData, esTimer)
            li = CSVWriter.formatData(liData, liTimer)
            lt = CSVWriter.formatData(ltData, ltTimer)

            #ls = ["wl"] + list(ds.m_data.dtype.names)

            CSVWriter.writeCSV(name, dirpath, es, "ES", level)
            CSVWriter.writeCSV(name, dirpath, li, "LI", level)
            CSVWriter.writeCSV(name, dirpath, lt, "LT", level)


    @staticmethod
    def removeColumns(a, removeNameList):
        return a[[name for name in a.dtype.names if name not in removeNameList]]


    @staticmethod
    def outputTXT_L2s(fp):
        CSVWriter.outputTXT_Type2(fp, "L2s")

    @staticmethod
    def outputTXT_L3a(fp):
        CSVWriter.outputTXT_Type2(fp, "L3a")

    @staticmethod
    def outputTXT_Type2(fp, level):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]

        filepath = os.path.join(dirpath, filename + "_" + level +".hdf")
        if not os.path.isfile(filepath):
            return

        root = HDFRoot.readHDF5(filepath)
        if root is None:
            print("outputCSV: root is None")
            return

        dirpath = "csv"
        #name = filename[28:43]
        name = filename[0:15]

        referenceGroup = root.getGroup("Reference")
        sasGroup = root.getGroup("SAS")

        esData = referenceGroup.getDataset("ES_hyperspectral")
        liData = sasGroup.getDataset("LI_hyperspectral")
        ltData = sasGroup.getDataset("LT_hyperspectral")

        esTT2 = esData.m_data["Timetag2"]
        liTT2 = liData.m_data["Timetag2"]
        ltTT2 = ltData.m_data["Timetag2"]

        esData = CSVWriter.removeColumns(esData.m_data, ["Datetag", "Timetag2"])
        liData = CSVWriter.removeColumns(liData.m_data, ["Datetag", "Timetag2"])
        ltData = CSVWriter.removeColumns(ltData.m_data, ["Datetag", "Timetag2"])

        es = CSVWriter.formatData2(esData, esTT2)
        li = CSVWriter.formatData2(liData, liTT2)
        lt = CSVWriter.formatData2(ltData, ltTT2)

        CSVWriter.writeCSV(name, dirpath, es, "ES", level)
        CSVWriter.writeCSV(name, dirpath, li, "LI", level)
        CSVWriter.writeCSV(name, dirpath, lt, "LT", level)



    @staticmethod
    def outputTXT_L4(fp):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]

        filepath = os.path.join(dirpath, filename + "_L4.hdf")
        if not os.path.isfile(filepath):
            return

        root = HDFRoot.readHDF5(filepath)
        if root is None:
            print("outputCSV: root is None")
            return

        dirpath = "csv"
        #name = filename[28:43]
        name = filename[0:15]

        gp = root.getGroup("Reflectance")

        esData = gp.getDataset("ES")
        liData = gp.getDataset("LI")
        ltData = gp.getDataset("LT")
        rrsData = gp.getDataset("Rrs")

        
        CSVWriter.writeCSV(name, dirpath, esData.m_data, "ES", "L4")
        CSVWriter.writeCSV(name, dirpath, liData.m_data, "LI", "L4")
        CSVWriter.writeCSV(name, dirpath, ltData.m_data, "LT", "L4")
        CSVWriter.writeCSV(name, dirpath, rrsData.m_data, "RRS", "L4")


