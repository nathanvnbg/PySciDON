
import os
import shutil
import sys
#from PyQt4 import QtCore, QtGui
from PyQt5 import QtCore, QtGui, QtWidgets

from Controller import Controller

from ConfigFile import ConfigFile
from ConfigWindow import ConfigWindow

from PreprocessRawFile import PreprocessRawFile

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
        
        # Create folders if they don't exist
        #if not os.path.exists("RawData"):
        #    os.makedirs("RawData")
        #if not os.path.exists("Data"):
        #    os.makedirs("Data")
        #if not os.path.exists("Plots"):
        #    os.makedirs("Plots")
        #if not os.path.exists("csv"):
        #    os.makedirs("csv")
        if not os.path.exists("Config"):
            os.makedirs("Config")

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
        configPath = os.path.join("Config", configFileName)
        if os.path.isfile(configPath):
            ConfigFile.loadConfig(configFileName)
            configDialog = ConfigWindow(configFileName, self)
            #configDialog = CalibrationEditWindow(configFileName, self)
            configDialog.show()
        else:
            #print("Not a Config File: " + configFileName)
            message = "Not a Config File: " + configFileName
            QtWidgets.QMessageBox.critical(self, "Error", message)


    def configDeleteButtonPressed(self):
        print("Delete Config Dialogue")
        print("index: ", self.configComboBox.currentIndex())
        print("text: ", self.configComboBox.currentText())
        configFileName = self.configComboBox.currentText()
        configPath = os.path.join("Config", configFileName)
        if os.path.isfile(configPath):
            configDeleteMessage = "Delete " + configFileName + "?"

            reply = QtWidgets.QMessageBox.question(self, 'Message', configDeleteMessage, \
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                ConfigFile.deleteConfig(configFileName)
        else:
            #print("Not a Config File: " + configFileName)
            message = "Not a Config File: " + configFileName
            QtWidgets.QMessageBox.critical(self, "Error", message)


    def windAddButtonPressed(self):
        print("Wind File Add Dialogue")
        fnames = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Wind File")
        print(fnames)
        if len(fnames[0]) == 1:
            self.windFileLineEdit.setText(fnames[0][0])

    def windRemoveButtonPressed(self):
        print("Wind File Remove Dialogue")
        self.windFileLineEdit.setText("")


    # Backup files before preprocessing if source files same as output directory
    def createBackupFiles(self, fileNames, dataDirectory):
        if len(fileNames) > 0:
            path = fileNames[0]
            (dirPath, fileName) = os.path.split(path)
            if dirPath == dataDirectory:
                newFileNames = []
                backupDir = os.path.join(dataDirectory, "Backup")
                if not os.path.exists(backupDir):
                    os.makedirs(backupDir)
                for path in fileNames:
                    (dirPath, fileName) = os.path.split(path)
                    backupPath = os.path.join(backupDir, fileName)
                    if not os.path.exists(backupPath):
                        shutil.move(path, backupPath)
                    newFileNames.append(backupPath)
                fileNames = newFileNames
        return fileNames

    def processSingle(self, level):
        print("Process Single-Level")

        # Load Config file
        configFileName = self.configComboBox.currentText()
        configPath = os.path.join("Config", configFileName)
        if not os.path.isfile(configPath):
            message = "Not valid Config File: " + configFileName
            QtWidgets.QMessageBox.critical(self, "Error", message)
            return
        ConfigFile.loadConfig(configFileName)

        # Select data files
        openFileNames = QtWidgets.QFileDialog.getOpenFileNames(self, "Open File")
        print("Files:", openFileNames)
        if not openFileNames[0]:
            return
        fileNames = openFileNames[0]
        #calibrationDirectory = settings["sCalibrationFolder"].strip('"')
        #preprocessDirectory = settings["sPreprocessFolder"].strip('"')

        windFile = self.windFileLineEdit.text()

        print("Process Calibration Files")
        #calibrationMap = Controller.processCalibration(calibrationDirectory)
        filename = ConfigFile.filename
        calFiles = ConfigFile.settings["CalibrationFiles"]
        calibrationMap = Controller.processCalibrationConfig(filename, calFiles)

        if level == "0":
            # Select Output Directory
            dataDirectory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
            print("Output Directory:", dataDirectory)
            if not dataDirectory[0]:
                return

            # Copy to backup folder if same directory
            fileNames = self.createBackupFiles(fileNames, dataDirectory)


            print("Preprocess Raw Files")
            checkCoords = int(ConfigFile.settings["bL0CheckCoords"])
            startLongitude = float(ConfigFile.settings["fL0LonMin"])
            endLongitude = float(ConfigFile.settings["fL0LonMax"])
            direction = ConfigFile.settings["cL0Direction"]
            cleanRotatorAngle = int(ConfigFile.settings["bL0CleanRotatorAngle"])
            cleanSunAngle = int(ConfigFile.settings["bL0CleanSunAngle"])
            angleMin = float(ConfigFile.settings["fL0SunAngleMin"])
            angleMax = float(ConfigFile.settings["fL0SunAngleMax"])
            rotatorAngleMin = float(ConfigFile.settings["fL0RotatorAngleMin"])
            rotatorAngleMax = float(ConfigFile.settings["fL0RotatorAngleMax"])
            rotatorHomeAngle = float(ConfigFile.settings["fL0RotatorHomeAngle"])
            rotatorDelay = float(ConfigFile.settings["fL0RotatorDelay"])
            splitRawFile = int(ConfigFile.settings["bL0SplitRawFile"])
            #rotatorDelay = 60
            print("Preprocess Longitude Data", startLongitude, endLongitude, direction)
            #Controller.preprocessData(preprocessDirectory, dataDirectory, calibrationMap, \
            #                          checkCoords, startLongitude, endLongitude, direction, \
            #                          doCleaning, angleMin, angleMax)
            PreprocessRawFile.processFiles(fileNames, dataDirectory, calibrationMap, \
                                      checkCoords, startLongitude, endLongitude, direction, \
                                      cleanRotatorAngle, cleanSunAngle, angleMin, angleMax, \
                                      rotatorAngleMin, rotatorAngleMax, rotatorHomeAngle, rotatorDelay,
                                      splitRawFile)
        else:
            print("Process Raw Files")
            Controller.processFilesSingleLevel(fileNames, calibrationMap, level, windFile)

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

        # Load Config file
        configFileName = self.configComboBox.currentText()
        configPath = os.path.join("Config", configFileName)
        if not os.path.isfile(configPath):
            message = "Not valid Config File: " + configFileName
            QtWidgets.QMessageBox.critical(self, "Error", message)
            return
        ConfigFile.loadConfig(configFileName)

        # Select data files
        openFileNames = QtWidgets.QFileDialog.getOpenFileNames(self, "Open File")
        print("Files:", openFileNames)
        if not openFileNames[0]:
            return
        fileNames = openFileNames[0]
        #calibrationDirectory = settings["sCalibrationFolder"].strip('"')
        #preprocessDirectory = settings["sPreprocessFolder"].strip('"')


        # Select Output Directory
        dataDirectory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        print("Output Directory:", dataDirectory)
        if not dataDirectory:
            return


        # Copy to backup folder if same directory
        fileNames = self.createBackupFiles(fileNames, dataDirectory)


        windFile = self.windFileLineEdit.text()

        print("Process Calibration Files")
        filename = ConfigFile.filename
        calFiles = ConfigFile.settings["CalibrationFiles"]
        calibrationMap = Controller.processCalibrationConfig(filename, calFiles)

        print("Preprocess Raw Files")
        checkCoords = int(ConfigFile.settings["bL0CheckCoords"])
        startLongitude = float(ConfigFile.settings["fL0LonMin"])
        endLongitude = float(ConfigFile.settings["fL0LonMax"])
        direction = ConfigFile.settings["cL0Direction"]
        print("Preprocess Longitude Data", startLongitude, endLongitude, direction)
        cleanRotatorAngle = int(ConfigFile.settings["bL0CleanRotatorAngle"])
        cleanSunAngle = int(ConfigFile.settings["bL0CleanSunAngle"])
        angleMin = float(ConfigFile.settings["fL0SunAngleMin"])
        angleMax = float(ConfigFile.settings["fL0SunAngleMax"])
        splitRawFile = int(ConfigFile.settings["bL0SplitRawFile"])
        print("Preprocess Angle Data", cleanSunAngle, cleanRotatorAngle, angleMin, angleMax)
        rotatorAngleMin = float(ConfigFile.settings["fL0RotatorAngleMin"])
        rotatorAngleMax = float(ConfigFile.settings["fL0RotatorAngleMax"])
        rotatorHomeAngle = float(ConfigFile.settings["fL0RotatorHomeAngle"])
        rotatorDelay = float(ConfigFile.settings["fL0RotatorDelay"])
        print("Preprocess Rotator Data", rotatorAngleMin, rotatorAngleMax, rotatorHomeAngle, rotatorDelay)
        #Controller.preprocessData(preprocessDirectory, dataDirectory, calibrationMap, \
        #                          checkCoords, startLongitude, endLongitude, direction, \
        #                          doCleaning, angleMin, angleMax)
        files = PreprocessRawFile.processFiles(fileNames, dataDirectory, calibrationMap, \
                                  checkCoords, startLongitude, endLongitude, direction, \
                                  cleanRotatorAngle, cleanSunAngle, angleMin, angleMax, \
                                  rotatorAngleMin, rotatorAngleMax, rotatorHomeAngle, rotatorDelay, \
                                  splitRawFile)
        print("Process Raw Files")
        #print(files)
        #Controller.processDirectory(dataDirectory, calibrationMap, level, windFile)
        Controller.processFilesMultiLevel(files, calibrationMap, level, windFile)

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
