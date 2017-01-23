
import os
import sys
import shutil
#from PyQt4 import QtCore, QtGui
from PyQt5 import QtCore, QtGui, QtWidgets

from Controller import Controller
from config import settings

from ConfigFile import ConfigFile
from ConfigWindow import ConfigWindow

#from CalibrationEditWindow import CalibrationEditWindow

'''
class ConfigWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.initUI()

    def initUI(self):
        self.label = QtWidgets.QLabel("Popup", self)
        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Config')
        #self.show()
'''

#class Window(QtGui.QWidget):
class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        fsm = QtWidgets.QFileSystemModel()
        index = fsm.setRootPath("Config")


        self.configLabel = QtWidgets.QLabel('Config File', self)
        #self.configLabel.move(30, 20)

        self.configComboBox = QtWidgets.QComboBox(self)
        self.configComboBox.setModel(fsm)
        fsm.setNameFilters(["*.cfg"])
        fsm.setNameFilterDisables(False)
        fsm.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)
        self.configComboBox.setRootModelIndex(index)
        #self.configComboBox.addItem("1")
        #self.configComboBox.addItem("A")
        #self.configComboBox.addItem("qwerty")
        #self.configComboBox.move(30, 50)


        self.configNewButton = QtWidgets.QPushButton("New", self)
        #self.configNewButton.move(30, 80)

        self.configEditButton = QtWidgets.QPushButton("Edit", self)
        #self.configEditButton.move(130, 80)

        self.configDeleteButton = QtWidgets.QPushButton("Delete", self)

        
        self.windFileLabel = QtWidgets.QLabel("Wind Speed File")
        self.windFileLineEdit = QtWidgets.QLineEdit()
        self.windAddButton = QtWidgets.QPushButton("Add", self)
        self.windRemoveButton = QtWidgets.QPushButton("Remove", self)
        

        self.configNewButton.clicked.connect(self.configNewButtonPressed)
        self.configEditButton.clicked.connect(self.configEditButtonPressed)
        self.configDeleteButton.clicked.connect(self.configDeleteButtonPressed)


        self.windAddButton.clicked.connect(self.windAddButtonPressed)
        self.windRemoveButton.clicked.connect(self.windRemoveButtonPressed)


        self.singleLevelLabel = QtWidgets.QLabel('Single-Level Processing', self)
        #self.singleLevelLabel.move(30, 270)


        self.singleL0Button = QtWidgets.QPushButton("Preprocess Raw", self)
        #self.singleL0Button.move(30, 300)

        self.singleL1aButton = QtWidgets.QPushButton("Level 1 --> 1a", self)
        #self.singleL1aButton.move(30, 350)

        self.singleL1bButton = QtWidgets.QPushButton("Level 1a --> 1b", self)
        #self.singleL1bButton.move(30, 400)

        self.singleL2Button = QtWidgets.QPushButton("Level 1b --> 2", self)
        #self.singleL2Button.move(30, 450)

        self.singleL2sButton = QtWidgets.QPushButton("Level 2 --> 2s", self)
        #self.singleL2sButton.move(30, 500)

        self.singleL3aButton = QtWidgets.QPushButton("Level 2s --> 3a", self)
        #self.singleL3aButton.move(30, 550)

        self.singleL4Button = QtWidgets.QPushButton("Level 3a --> 4", self)
        #self.singleL4Button.move(30, 600)


        self.singleL0Button.clicked.connect(self.singleL0Clicked)
        self.singleL1aButton.clicked.connect(self.singleL1aClicked)
        self.singleL1bButton.clicked.connect(self.singleL1bClicked)            
        self.singleL2Button.clicked.connect(self.singleL2Clicked)
        self.singleL2sButton.clicked.connect(self.singleL2sClicked)            
        self.singleL3aButton.clicked.connect(self.singleL3aClicked)
        self.singleL4Button.clicked.connect(self.singleL4Clicked)            



        self.multiLevelLabel = QtWidgets.QLabel('Multi-Level Processing', self)
        #self.multiLevelLabel.move(30, 140)


        self.multi1Button = QtWidgets.QPushButton("Level 1 --> 2", self)
        #self.multi1Button.move(30, 170)

        self.multi2Button = QtWidgets.QPushButton("Level 1 --> 2s", self)
        #self.multi2Button.move(30, 220)

        self.multi3Button = QtWidgets.QPushButton("Level 1 --> 3a", self)
        #self.multi3Button.move(30, 270)

        self.multi4Button = QtWidgets.QPushButton("Level 1 --> 4", self)
        #self.multi4Button.move(30, 320)

        self.multi1Button.clicked.connect(self.multi1Clicked)
        self.multi2Button.clicked.connect(self.multi2Clicked)
        self.multi3Button.clicked.connect(self.multi3Clicked)
        self.multi4Button.clicked.connect(self.multi4Clicked)



        vBox = QtWidgets.QVBoxLayout()

        vBox.addStretch(1)

        vBox.addWidget(self.configLabel)
        vBox.addWidget(self.configComboBox)

        configHBox = QtWidgets.QHBoxLayout()
        configHBox.addWidget(self.configNewButton)
        configHBox.addWidget(self.configEditButton)
        configHBox.addWidget(self.configDeleteButton)

        vBox.addLayout(configHBox)


        vBox.addStretch(1)

        vBox.addWidget(self.windFileLabel)
        
        vBox.addWidget(self.windFileLineEdit)

        windHBox = QtWidgets.QHBoxLayout()        
        windHBox.addWidget(self.windAddButton)
        windHBox.addWidget(self.windRemoveButton)

        vBox.addLayout(windHBox)


        vBox.addStretch(1)

        vBox.addWidget(self.singleLevelLabel)
        vBox.addWidget(self.singleL0Button)
        vBox.addWidget(self.singleL1aButton)
        vBox.addWidget(self.singleL1bButton)
        vBox.addWidget(self.singleL2Button)
        vBox.addWidget(self.singleL2sButton)
        vBox.addWidget(self.singleL3aButton)
        vBox.addWidget(self.singleL4Button)

        vBox.addStretch(1)

        vBox.addWidget(self.multiLevelLabel)
        vBox.addWidget(self.multi1Button)
        vBox.addWidget(self.multi2Button)        
        vBox.addWidget(self.multi3Button)
        vBox.addWidget(self.multi4Button)

        vBox.addStretch(1)

        self.setLayout(vBox)

        self.setGeometry(300, 300, 290, 600)
        self.setWindowTitle('PySciDON')
        self.show()


    def configNewButtonPressed(self):
        print("New Config Dialogue")
        text, ok = QtWidgets.QInputDialog.getText(self, 'New Config File', 'Enter File Name')
        if ok:
            print("Create Config File: ", text)
            ConfigFile.createDefaultConfig(text)
            # ToDo: Add code to change text for the combobox once file is created


    def configEditButtonPressed(self):
        print("Edit Config Dialogue")
        print("index: ", self.configComboBox.currentIndex())
        print("text: ", self.configComboBox.currentText())
        configFileName = self.configComboBox.currentText()
        ConfigFile.loadConfig(configFileName)
        configDialog = ConfigWindow(configFileName, self)
        #configDialog = CalibrationEditWindow(configFileName, self)
        configDialog.show()

    def configDeleteButtonPressed(self):
        print("Delete Config Dialogue")
        print("index: ", self.configComboBox.currentIndex())
        print("text: ", self.configComboBox.currentText())
        configFileName = self.configComboBox.currentText()
        configDeleteMessage = "Delete " + configFileName + "?"

        reply = QtWidgets.QMessageBox.question(self, 'Message', configDeleteMessage, \
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            ConfigFile.deleteConfig(configFileName)


    def windAddButtonPressed(self):
        print("Wind File Add Dialogue")
        fnames = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Wind File")
        print(fnames)
        if len(fnames[0]) == 1:
            self.windFileLineEdit.setText(fnames[0][0])

    def windRemoveButtonPressed(self):
        print("Wind File Remove Dialogue")
        self.windFileLineEdit.setText("")


    def copyPreprocessFiles(self, files):
        preprocessFolder= settings["sPreprocessFolder"].strip('"')
        cwd = os.getcwd()
        preprocessDirectory = os.path.join(cwd, preprocessFolder)
        
        for fp in files:
            (dirpath, filename) = os.path.split(fp)
            newfp = os.path.join(preprocessDirectory, filename)
            shutil.copy(fp, newfp)

    def processSingle(self, level):
        print("Process Single-Level")
        configFileName = self.configComboBox.currentText()
        ConfigFile.loadConfig(configFileName)
        fnames = QtWidgets.QFileDialog.getOpenFileNames(self, "Open File")
        print("Files:", fnames)
        #calibrationDirectory = settings["sCalibrationFolder"].strip('"')
        preprocessDirectory = settings["sPreprocessFolder"].strip('"')
        dataDirectory = settings["sProcessDataFolder"].strip('"')

        windFile = self.windFileLineEdit.text()

        print("Process Calibration Files")
        #calibrationMap = Controller.processCalibration(calibrationDirectory)
        filename = ConfigFile.filename
        calFiles = ConfigFile.settings["CalibrationFiles"]
        calibrationMap = Controller.processCalibrationConfig(filename, calFiles)

        if level == "0":
            self.copyPreprocessFiles(fnames[0])

            print("Preprocess Raw Files")
            checkCoords = int(ConfigFile.settings["bL0CheckCoords"])
            startLongitude = float(ConfigFile.settings["fL0LonMin"])
            endLongitude = float(ConfigFile.settings["fL0LonMax"])
            direction = ConfigFile.settings["cL0Direction"]
            doCleaning = int(ConfigFile.settings["bL0PerformCleaning"])
            angleMin = float(ConfigFile.settings["fL0AngleMin"])
            angleMax = float(ConfigFile.settings["fL0AngleMax"])
            print(startLongitude, endLongitude, direction)
            Controller.preprocessData(preprocessDirectory, dataDirectory, calibrationMap, \
                                      checkCoords, startLongitude, endLongitude, direction, \
                                      doCleaning, angleMin, angleMax)
        else:
            print("Process Raw Files")
            Controller.processFilesSingleLevel(fnames[0], calibrationMap, level, windFile)

    def singleL0Clicked(self):
        self.processSingle("0")

    def singleL1aClicked(self):
        self.processSingle("1a")

    def singleL1bClicked(self):
        self.processSingle("1b")

    def singleL2Clicked(self):
        self.processSingle("2")

    def singleL2sClicked(self):
        self.processSingle("2s")

    def singleL3aClicked(self):
        self.processSingle("3a")

    def singleL4Clicked(self):
        self.processSingle("4")


    def processMulti(self, level):
        print("Process Multi-Level")
        configFileName = self.configComboBox.currentText()
        ConfigFile.loadConfig(configFileName)
        fnames = QtWidgets.QFileDialog.getOpenFileNames(self, "Open File")
        print("Files:", fnames)
        #calibrationDirectory = settings["sCalibrationFolder"].strip('"')
        preprocessDirectory = settings["sPreprocessFolder"].strip('"')
        dataDirectory = settings["sProcessDataFolder"].strip('"')

        windFile = self.windFileLineEdit.text()

        self.copyPreprocessFiles(fnames[0])

        print("Process Calibration Files")
        filename = ConfigFile.filename
        calFiles = ConfigFile.settings["CalibrationFiles"]
        calibrationMap = Controller.processCalibrationConfig(filename, calFiles)

        print("Preprocess Raw Files")
        checkCoords = int(ConfigFile.settings["bL0CheckCoords"])
        startLongitude = float(ConfigFile.settings["fL0LonMin"])
        endLongitude = float(ConfigFile.settings["fL0LonMax"])
        direction = ConfigFile.settings["cL0Direction"]
        print(startLongitude, endLongitude, direction)
        doCleaning = int(ConfigFile.settings["bL0PerformCleaning"])
        angleMin = float(ConfigFile.settings["fL0AngleMin"])
        angleMax = float(ConfigFile.settings["fL0AngleMax"])
        print(doCleaning, angleMin, angleMax)
        Controller.preprocessData(preprocessDirectory, dataDirectory, calibrationMap, \
                                  checkCoords, startLongitude, endLongitude, direction, \
                                  doCleaning, angleMin, angleMax)
        print("Process Raw Files")
        Controller.processDirectory(dataDirectory, calibrationMap, level, windFile)
        #Controller.processFilesMultiLevel(fnames[0], calibrationMap, level)

    def multi1Clicked(self):
        self.processMulti(1)

    def multi2Clicked(self):
        self.processMulti(2)

    def multi3Clicked(self):
        self.processMulti(3)

    def multi4Clicked(self):
        self.processMulti(4)


if __name__ == '__main__':
    #app = QtGui.QApplication(sys.argv)
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())

'''
import sys
from PyQt4 import QtGui

from Controller import Controller
from PreprocessRawFile import PreprocessRawFile


def main():
    #print("test:", float(b"+12.69"))
    calibrationMap = Controller.processCalibration("Calibration")
    #PreprocessRawFile.processDirectory("RawData", calibrationMap, 12317.307, 12356.5842, 'E')
    Controller.processDirectory("Data", calibrationMap)


if __name__ == "__main__":
    main()
'''
