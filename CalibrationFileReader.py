
import os.path
import zipfile

#from CalibrationData import CalibrationData
from CalibrationFile import CalibrationFile


class CalibrationFileReader:

    @staticmethod
    def read(fp):
        calibrationMap = {}

        with zipfile.ZipFile(fp, 'r') as zf:
            for finfo in zf.infolist():
                #print("infile:", finfo.filename)
                if os.path.splitext(finfo.filename)[1].lower() == ".cal" or \
                   os.path.splitext(finfo.filename)[1].lower() == ".tdf":
                    with zf.open(finfo) as f:
                        cf = CalibrationFile()
                        cf.read(f)
                        #print("id:", cf.m_id)
                        calibrationMap[cf.m_id] = cf

        return calibrationMap
