
#import collections
#import time
#from datetime import datetime

import os
#import os.path
#import zipfile
import sys

from PyQt4.QtCore import pyqtSlot
from PyQt4 import QtGui

import h5py
import numpy as np
#import scipy as sp
from scipy import interpolate

#from CalibrationData import CalibrationData
#from CalibrationFile import CalibrationFile
from CalibrationFileReader import CalibrationFileReader
from RawFileReader import RawFileReader
from HDFRoot import HDFRoot
from HDFGroup import HDFGroup
from HDFDataset import HDFDataset


class Controller:
    @staticmethod
    def generateContext(calibrationMap):
        for key in calibrationMap:
            cf = calibrationMap[key]
            if cf.m_id == "SATHED0150":
                cf.m_instrumentType = "Reference"
                cf.m_media = "Air"
                cf.m_measMode = "Surface"
                cf.m_frameType = "ShutterDark"
                cf.m_sensorType = "ES"
            elif cf.m_id == "SATHLD0151":
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "ShutterDark"
                cf.m_sensorType = "LI"
            elif cf.m_id == "SATHLD0152":
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "ShutterDark"
                cf.m_sensorType = "LT"
            elif cf.m_id == "SATHSE0150":
                cf.m_instrumentType = "Reference"
                cf.m_media = "Air"
                cf.m_measMode = "Surface"
                cf.m_frameType = "ShutterLight"
                cf.m_sensorType = "ES"
            elif cf.m_id == "SATHSL0151":
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "ShutterLight"
                cf.m_sensorType = "LI"
            elif cf.m_id == "SATHSL0152":
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "ShutterLight"
                cf.m_sensorType = "LT"
            elif cf.m_id == "SATSAS0052":
                cf.m_instrumentType = "SAS"
                cf.m_media = "Air"
                cf.m_measMode = "VesselBorne"
                cf.m_frameType = "LightAncCombined"
                cf.m_sensorType = "None"
            elif cf.m_id == "$GPRMC":
                cf.m_instrumentType = "GPS"
                cf.m_media = "Not Required"
                cf.m_measMode = "Not Required"
                cf.m_frameType = "Not Required"
                cf.m_sensorType = "None"

    @staticmethod
    def processCalibration(calPath):
        print("ReadCalibrationFile")
        calibrationMap = CalibrationFileReader.read(calPath)
        print("calibrationMap:", list(calibrationMap.keys()))
        Controller.generateContext(calibrationMap)
        return calibrationMap


    @staticmethod
    def process(fp, calibrationMap):
        (dirpath, filename) = os.path.split(fp)
        filename = os.path.splitext(filename)[0]

        root = HDFRoot()


        print("ProcessL1a")
        #root = RawFileReader.readRawFile("data.raw", calibrationMap)
        #generateContext(root)
        #print("HDFFile:")
        #root.prnt()
        fp = os.path.join(dirpath, filename + ".raw")
        root = root.processL1a(calibrationMap, fp)
        fp = os.path.join(dirpath, filename + "_L1a.hdf")
        root.writeHDF5(fp)
        #fp = os.path.join(dirpath, filename + "_L1a.hdf4")
        #if os.path.exists(fp):
        #    os.remove(fp)
        #root.writeHDF4(fp)


        print("ProcessL1b")
        root = HDFRoot.readHDF5(os.path.join(dirpath, filename + "_L1a.hdf"))
        #print("HDFFile:")
        #root.prnt()
        root = root.processL1b(calibrationMap)
        root.writeHDF5(os.path.join(dirpath, filename + "_L1b.hdf"))


        print("ProcessL2")
        root = HDFRoot.readHDF5(os.path.join(dirpath, filename + "_L1b.hdf"))
        #root.processTIMER()
        root = root.processL2()
        root.writeHDF5(os.path.join(dirpath, filename + "_L2.hdf"))


        print("ProcessL2s")
        root = HDFRoot.readHDF5(os.path.join(dirpath, filename + "_L2.hdf"))
        #processGPSTime(root)
        root = root.processL2s()
        #root.prnt()
        root.writeHDF5(os.path.join(dirpath, filename + "_L2s.hdf"))


        print("ProcessL3a")
        root = HDFRoot.readHDF5(os.path.join(dirpath, filename + "_L2s.hdf"))
        root = root.processL3a()
        root.writeHDF5(os.path.join(dirpath, filename + "_L3a.hdf"))


        root = HDFRoot.readHDF5(os.path.join(dirpath, filename + "_L3a.hdf"))

    @staticmethod
    def processDirectory(path, calibrationMap):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for name in filenames:
                #print("infile:", name)
                if os.path.splitext(name)[1].lower() == ".raw":
                    Controller.process(os.path.join(dirpath, name), calibrationMap)
            break



class CalibrationConfigWidget(QtGui.QWidget):

    def __init__(self):
        super(CalibrationConfigWidget, self).__init__()
        self.initUI()

    def closeButtonClicked(self):
        self.close()

    def listWidgetClicked(self,item):
        QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())

    def initUI(self):
        vbox = QtGui.QVBoxLayout()

        lSensors = QtGui.QLabel()
        lSensors.setText("Sensors")
        vbox.addWidget(lSensors)
    
        lFrameTag = QtGui.QLabel()
        lFrameTag.setText("Frame Tag")
        vbox.addWidget(lFrameTag)

        lFrameTag2 = QtGui.QLabel()
        lFrameTag2.setText("Frame Tag")
        lFrameTag2.setStyleSheet("QLabel { background-color : white; color : black; }")
        vbox.addWidget(lFrameTag2)
    
        lInstrumentType = QtGui.QLabel()
        lInstrumentType.setText("Instrument Type")
        vbox.addWidget(lInstrumentType)

        cb = QtGui.QComboBox()
        cb.addItems(["1", "2", "3"])
        #cb.currentIndexChanged.connect(self.selectionchange)
        vbox.addWidget(cb)

        lImmersionCoefficient = QtGui.QLabel()
        lImmersionCoefficient.setText("Immersion Coefficient")
        vbox.addWidget(lImmersionCoefficient)

        lMeasurementMode = QtGui.QLabel()
        lMeasurementMode.setText("Measurement Mode")
        vbox.addWidget(lMeasurementMode)

        lFrameType = QtGui.QLabel()
        lFrameType.setText("Frame Type")
        vbox.addWidget(lFrameType)
        
        closeButton = QtGui.QPushButton("Close")
        closeButton.clicked.connect(self.closeButtonClicked)
        vbox.addWidget(closeButton)


        hbox = QtGui.QHBoxLayout()
    
        self.listWidget = QtGui.QListWidget()
        self.listWidget.resize(200,120)
        self.listWidget.itemClicked.connect(self.listWidgetClicked)

        hbox.addWidget(self.listWidget)
        hbox.addStretch()
        hbox.addLayout(vbox)
    
        self.setLayout(hbox)
    
        self.setWindowTitle("PyQt")



class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.calConfig = CalibrationConfigWidget()
        self.calPath = ""
        self.rawPath = ""
        self.initUI()

    def initUI(self):
        bSelectCal = QtGui.QPushButton(self)
        bSelectCal.setText("Select Calibration Folder")
        bSelectCal.resize(bSelectCal.sizeHint())
        bSelectCal.move(20,40)
        bSelectCal.clicked.connect(self.selectCalDialog) 

        bSelectRaw = QtGui.QPushButton(self)
        bSelectRaw.setText("Process Raw Files")
        bSelectRaw.resize(bSelectRaw.sizeHint())
        bSelectRaw.move(20,120)
        bSelectRaw.clicked.connect(self.selectRawDialog)  

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Test')
        self.show()

    def selectCalDialog(self):
        #fp = QtGui.QFileDialog.getOpenFileName(self, 'Open file',  '/home')
        self.calPath = QtGui.QFileDialog.getExistingDirectory(self, "Select Calibration Directory")#,  '/home/spectral/SCS')
        print("Calibration Directory:", self.calPath)
        self.calibrationMap = Controller.processCalibration(self.calPath)

        items = [self.calibrationMap[k].m_name for k in self.calibrationMap]
        
        self.calConfig.listWidget.clear()
        self.calConfig.listWidget.addItems(items)
        self.calConfig.show()


    def selectRawDialog(self):
        self.rawPath = QtGui.QFileDialog.getExistingDirectory(self, "Select Raw File Directory")#,  '/home/spectral/SCS')
        print("Raw File Directory:", self.rawPath)
        Controller.processDirectory(self.rawPath, self.calibrationMap)

#        f = open(fname, 'r')
#        with f:        
#            data = f.read()
#            self.textEdit.setText(data) 


def main():
    app = QtGui.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())


#def main():
#    calibrationMap = processCalibration("Calibration")
#    Controller.processDirectory("Data", calibrationMap)

if __name__ == "__main__":
    main()
