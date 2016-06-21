
import collections
import os
#import sys

from PyQt4.QtCore import pyqtSlot
from PyQt4 import QtGui

from Controller import Controller


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


    def selectionchange(self,i):
        #print("Items in the list are :")
        #for count in range(self.frameTypeComboBox.count()):
        #    print(self.frameTypeComboBox.itemText(count))
        #print("Current index",i,"selection changed ",self.frameTypeComboBox.currentText())
        name = self.listWidget.currentItem().text()
        cf = self.calibrationMap[name]
        cf.m_frameType = self.frameTypeComboBox.currentText()
        #print(name, cf.m_frameType)


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
        #self.instrumentTypeComboBox.currentIndexChanged.connect(self.selectionchange)
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
        self.frameTypeComboBox.currentIndexChanged.connect(self.selectionchange)
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


#def main():
#    app = QtGui.QApplication(sys.argv)
#    win = Window()
#    sys.exit(app.exec_())

def main():
    calibrationMap = Controller.processCalibration("Calibration")
    Controller.processDirectory("Data", calibrationMap)


'''
import numpy as np
import matplotlib.pyplot as plt

def main():
    font = {'family': 'serif',
        'color':  'darkred',
        'weight': 'normal',
        'size': 16,
        }

    x = np.linspace(0.0, 5.0, 100)
    y = np.cos(2*np.pi*x) * np.exp(-x)

    plt.plot(x, y, 'k')
    plt.title('Damped exponential decay', fontdict=font)
    plt.text(2, 0.65, r'$\cos(2 \pi t) \exp(-t)$', fontdict=font)
    plt.xlabel('time (s)', fontdict=font)
    plt.ylabel('voltage (mV)', fontdict=font)

    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.15)
    #plt.show()
    plt.savefig('Plots/file.png')
    plt.close()
'''

'''
def main():
    a1 = collections.OrderedDict()
    a2 = collections.OrderedDict()
    a1["A"] = 1
    a1["B"] = 2
    a2["B"] = 4
    a2["C"] = 3

    k1 = a1.keys()
    k2 = a2.keys()

    intersect = [x for x in k1 if x in k2]
    k1diff = [x for x in k1 if x not in intersect]
    k2diff = [x for x in k2 if x not in intersect]

    print(intersect)
    print(k1diff)
    print(k2diff)
'''

if __name__ == "__main__":
    main()
