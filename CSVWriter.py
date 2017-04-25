
import csv
import os

from HDFRoot import HDFRoot


class CSVWriter:
    
    @staticmethod
    def formatData(ds, dsTimer):
        dataOut = []
        #columnName = dsName.lower()

        total = ds.data.shape[0]
        #ls = ["wl"] + [k for k,v in sorted(ds.data.dtype.fields.items(), key=lambda k: k[1])]
        ls = [""] + list(ds.data.dtype.names)
        dataOut.append(ls)
        for i in range(total):
            #n = str(i+1)
            #ls = [columnName + "_" + name + '_' + n] + ['%f' % num for num in ds.data[i]]
            #print(dsTimer.data["NONE"][i])
            ls = [dsTimer.data["NONE"][i]] + ['%f' % num for num in ds.data[i]]
            dataOut.append(ls)

        return dataOut


    @staticmethod
    def formatData2(data, timer):
        dataOut = []
        #columnName = dsName.lower()

        total = data.shape[0]
        #ls = ["wl"] + [k for k,v in sorted(ds.data.dtype.fields.items(), key=lambda k: k[1])]
        ls = [""] + list(data.dtype.names)
        dataOut.append(ls)
        for i in range(total):
            #n = str(i+1)
            #ls = [columnName + "_" + name + '_' + n] + ['%f' % num for num in ds.data[i]]
            #print(dsTimer.data["NONE"][i])
            ls = [timer[i]] + ['%f' % num for num in data[i]]
            dataOut.append(ls)

        return dataOut


    @staticmethod
    def writeCSV(name, dirpath, data, sensorName, level):
        filename = name + "_" + sensorName + "_" + level

        # Create output directory
        csvdir = os.path.join(dirpath, 'csv')
        os.makedirs(csvdir, exist_ok=True)

        csvPath = os.path.join(csvdir, filename + ".csv")
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

        #name = filename[28:43]
        name = filename[0:15]

        esData = None
        liData = None
        ltData = None

        for gp in root.groups:
            if gp.attributes["FrameType"] == "ShutterLight":
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

            #ls = ["wl"] + list(ds.data.dtype.names)

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

        #name = filename[28:43]
        name = filename[0:15]

        referenceGroup = root.getGroup("Reference")
        sasGroup = root.getGroup("SAS")

        esData = referenceGroup.getDataset("ES_hyperspectral")
        liData = sasGroup.getDataset("LI_hyperspectral")
        ltData = sasGroup.getDataset("LT_hyperspectral")

        esTT2 = esData.data["Timetag2"]
        liTT2 = liData.data["Timetag2"]
        ltTT2 = ltData.data["Timetag2"]

        esData = CSVWriter.removeColumns(esData.data, ["Datetag", "Timetag2"])
        liData = CSVWriter.removeColumns(liData.data, ["Datetag", "Timetag2"])
        ltData = CSVWriter.removeColumns(ltData.data, ["Datetag", "Timetag2"])

        es = CSVWriter.formatData2(esData, esTT2)
        li = CSVWriter.formatData2(liData, liTT2)
        lt = CSVWriter.formatData2(ltData, ltTT2)

        CSVWriter.writeCSV(name, dirpath, es, "ES", level)
        CSVWriter.writeCSV(name, dirpath, li, "LI", level)
        CSVWriter.writeCSV(name, dirpath, lt, "LT", level)



    @staticmethod
    def outputTXT_L4(fp):
        CSVWriter.outputTXT_Type3(fp, "L4")
        CSVWriter.outputTXT_Type3(fp, "L4-flags")


    @staticmethod
    def outputTXT_Type3(fp, level):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]

        filepath = os.path.join(dirpath, filename + "_" + level +".hdf")
        if not os.path.isfile(filepath):
            return

        root = HDFRoot.readHDF5(filepath)
        if root is None:
            print("outputCSV: root is None")
            return

        #name = filename[28:43]
        name = filename[0:15]

        gp = root.getGroup("Reflectance")

        esData = gp.getDataset("ES")
        liData = gp.getDataset("LI")
        ltData = gp.getDataset("LT")
        rrsData = gp.getDataset("Rrs")
        if esData is None or liData is None or ltData is None or rrsData is None:
            return
        CSVWriter.writeCSV(name, dirpath, esData.data, "ES", level)
        CSVWriter.writeCSV(name, dirpath, liData.data, "LI", level)
        CSVWriter.writeCSV(name, dirpath, ltData.data, "LT", level)
        CSVWriter.writeCSV(name, dirpath, rrsData.data, "RRS", level)


