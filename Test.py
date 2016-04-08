
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
        #calibrationMap = CalibrationFileReader.readSip("cal2013.sip")
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

    def setCalibrationMap(self, c):
        self.calibrationMap = c


    def closeButtonClicked(self):
        self.close()

    def setInstrumentTypeComboBox(self, value="Default"):
        self.instrumentTypeComboBox.clear()
        items = ["Profiler", "Reference", "TACCS", "SAS", "GPS", "ECO Series IOP"]
        self.instrumentTypeComboBox.addItems(items)

        if value != "Default":
            index = items.index(value)
            print(value, items, index)
            if index >= 0:
                self.instrumentTypeComboBox.setCurrentIndex(index)

    def setImmersionCoefficientComboBox(self, instrumentType, value="Default"):
        self.immersionCoefficientComboBox.clear()
        items = []
        if instrumentType == "Profiler":
            items = ["Water"]
        elif instrumentType == "Reference":
            items = ["Air", "Water"]
        elif instrumentType == "TACCS":
            items = ["Water"]
        elif instrumentType == "SAS":
            items = ["Air"]
        elif instrumentType == "GPS":
            items = ["Not Required"]
        elif instrumentType == "ECO Series IOP":
            items = ["Not Required"]
        self.immersionCoefficientComboBox.addItems(items)

        if value != "Default":
            index = items.index(value)
            print(value, items, index)
            if index >= 0:
                self.immersionCoefficientComboBox.setCurrentIndex(index)


    def setMeasurementModeComboBox(self, instrumentType, value="Default"):
        self.measurementModeComboBox.clear()
        items = []
        if instrumentType == "Profiler":
            items = ["Freefall"]
        elif instrumentType == "Reference":
            items = ["Surface", "Logger"]
        elif instrumentType == "TACCS":
            items = ["Chain"]
        elif instrumentType == "SAS":
            items = ["VesselBorne", "AirBorne"]
        elif instrumentType == "GPS":
            items = ["Not Required"]
        elif instrumentType == "ECO Series IOP":
            items = ["Freefall", "Surface"]
        self.measurementModeComboBox.addItems(items)

        if value != "Default":
            index = items.index(value)
            print(value, items, index)
            if index >= 0:
                self.measurementModeComboBox.setCurrentIndex(index)


    def setFrameTypeComboBox(self, instrumentType, value="Default"):
        self.frameTypeComboBox.clear()
        items = []
        if instrumentType == "Profiler":
            items = ["ShutterLight", "ShutterDark", "Anc", "LightAncCombined"]
            if value == "Default":
                value = "LightAncCombined"
        elif instrumentType == "Reference":
            items = ["ShutterLight", "ShutterDark", "Anc", "LightAncCombined"]
            if value == "Default":
                value = "LightAncCombined"
        elif instrumentType == "TACCS":
            items = ["LightAncCombined"]
        elif instrumentType == "SAS":
            items = ["ShutterLight", "ShutterDark", "Anc", "LightAncCombined"]
            if value == "Default":
                value = "LightAncCombined"
        elif instrumentType == "GPS":
            items = ["Not Required"]
        elif instrumentType == "ECO Series IOP":
            items = ["Not Required"]
        self.frameTypeComboBox.addItems(items)

        if value != "Default":
            index = items.index(value)
            print(value, items, index)
            if index >= 0:
                print("test")
                self.frameTypeComboBox.setCurrentIndex(index)



    def listWidgetClicked(self, item):
        print("List Clicked:", item.text())
        #QtGui.QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())

        cf = self.calibrationMap[item.text()]

        print("id", cf.m_id)
        self.frameTagLabel.setText(cf.m_id)


        print("instrumentType", cf.m_instrumentType)
        self.setInstrumentTypeComboBox(cf.m_instrumentType)

        print("immersionCoefficient", cf.m_media)
        self.setImmersionCoefficientComboBox(cf.m_instrumentType, cf.m_media)

        print("measurementMode", cf.m_measMode)
        self.setMeasurementModeComboBox(cf.m_instrumentType, cf.m_measMode)
    
        print("frameType", cf.m_frameType)
        self.setFrameTypeComboBox(cf.m_instrumentType, cf.m_frameType)


    def initUI(self):
        vbox = QtGui.QVBoxLayout()

        lSensors = QtGui.QLabel()
        lSensors.setText("Sensors")
        vbox.addWidget(lSensors)


        lFrameTag = QtGui.QLabel()
        lFrameTag.setText("Frame Tag")
        vbox.addWidget(lFrameTag)

        self.frameTagLabel = QtGui.QLabel()
        self.frameTagLabel.setText("Frame Tag Label")
        self.frameTagLabel.setStyleSheet("QLabel { background-color : white; color : black; }")
        vbox.addWidget(self.frameTagLabel)


        lInstrumentType = QtGui.QLabel()
        lInstrumentType.setText("Instrument Type")
        vbox.addWidget(lInstrumentType)

        self.instrumentTypeComboBox = QtGui.QComboBox()
        #self.instrumentTypeComboBox.addItems(["1", "2", "3"])
        #self.instrumentTypeComboBox.currentIndexChanged.connect(self.selectionchange)
        vbox.addWidget(self.instrumentTypeComboBox)


        lImmersionCoefficient = QtGui.QLabel()
        lImmersionCoefficient.setText("Immersion Coefficient")
        vbox.addWidget(lImmersionCoefficient)

        self.immersionCoefficientComboBox = QtGui.QComboBox()
        #self.immersionCoefficientComboBox.addItems(["1", "2", "3"])
        #self.immersionCoefficientComboBox.currentIndexChanged.connect(self.selectionchange)
        vbox.addWidget(self.immersionCoefficientComboBox)


        lMeasurementMode = QtGui.QLabel()
        lMeasurementMode.setText("Measurement Mode")
        vbox.addWidget(lMeasurementMode)

        self.measurementModeComboBox = QtGui.QComboBox()
        #self.measurementModeComboBox.addItems(["1", "2", "3"])
        #self.measurementModeComboBox.currentIndexChanged.connect(self.selectionchange)
        vbox.addWidget(self.measurementModeComboBox)


        lFrameType = QtGui.QLabel()
        lFrameType.setText("Frame Type")
        vbox.addWidget(lFrameType)

        self.frameTypeComboBox = QtGui.QComboBox()
        #self.frameTypeComboBox.addItems(["1", "2", "3"])
        #self.frameTypeComboBox.currentIndexChanged.connect(self.selectionchange)
        vbox.addWidget(self.frameTypeComboBox)


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
    
        self.setWindowTitle("Instrument Context")



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

        self.calConfig.setCalibrationMap(self.calibrationMap)

        items = [k for k in self.calibrationMap.keys()]
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
#    calibrationMap = Controller.processCalibration("Calibration")
#    Controller.processDirectory("Data", calibrationMap)

if __name__ == "__main__":
    main()
