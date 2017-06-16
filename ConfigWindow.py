
import os
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets


from ConfigFile import ConfigFile


#class myListWidget(QtWidgets.QListWidget):
#   def Clicked(self,item):
#      QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())


class ConfigWindow(QtWidgets.QDialog):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.name = name
        self.initUI()

    def initUI(self):
        print("ConfigWindow - initUI")
        #self.label = QtWidgets.QLabel("Popup", self)

        self.nameLabel = QtWidgets.QLabel("Editing: " + self.name, self)


        # Calibration Config Settings
        self.addCalibrationFileButton = QtWidgets.QPushButton("Add Calibration Files")
        self.addCalibrationFileButton.clicked.connect(self.addCalibrationFileButtonPressed)

        calFiles = ConfigFile.settings["CalibrationFiles"]
        print("Calibration Files:")
        self.calibrationFileComboBox = QtWidgets.QComboBox(self)
        for file in calFiles:
            print(file)
        self.calibrationFileComboBox.addItems(sorted(calFiles.keys()))
        fsm = QtWidgets.QFileSystemModel()
        fsm.setNameFilters(["*.cal", "*.tdf"])
        fsm.setNameFilterDisables(False)
        fsm.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)
        calibrationDir = os.path.splitext(self.name)[0] + "_Calibration"
        configPath = os.path.join("Config", calibrationDir)
        index = fsm.setRootPath(configPath)
        self.calibrationFileComboBox.setModel(fsm)
        self.calibrationFileComboBox.setRootModelIndex(index)
        self.calibrationFileComboBox.currentIndexChanged.connect(self.calibrationFileChanged)

        
        self.calibrationEnabledCheckBox = QtWidgets.QCheckBox("Enabled", self)
        self.calibrationEnabledCheckBox.stateChanged.connect(self.calibrationEnabledStateChanged)
        self.calibrationEnabledCheckBox.setEnabled(False)

        calibrationFrameTypeLabel = QtWidgets.QLabel("Frame Type:", self)
        self.calibrationFrameTypeComboBox = QtWidgets.QComboBox(self)
        self.calibrationFrameTypeComboBox.addItem("ShutterLight")
        self.calibrationFrameTypeComboBox.addItem("ShutterDark")
        self.calibrationFrameTypeComboBox.addItem("Not Required")
        self.calibrationFrameTypeComboBox.addItem("LightAncCombined")
        self.calibrationFrameTypeComboBox.currentIndexChanged.connect(self.calibrationFrameTypeChanged)
        self.calibrationFrameTypeComboBox.setEnabled(False)



        # Config File Settings
        intValidator = QtGui.QIntValidator()
        doubleValidator = QtGui.QDoubleValidator()

        l0CheckCoordsLabel = QtWidgets.QLabel("Enable Longitude/Direction Checking", self)
        self.l0CheckCoordsCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL0CheckCoords"]) == 1:
            self.l0CheckCoordsCheckBox.setChecked(True)

        lonMinLabel = QtWidgets.QLabel("Longitude Min", self)
        self.lonMinLineEdit = QtWidgets.QLineEdit(self)
        self.lonMinLineEdit.setText(str(ConfigFile.settings["fL0LonMin"]))
        self.lonMinLineEdit.setValidator(doubleValidator)

        lonMaxLabel = QtWidgets.QLabel("Longitude Max", self)
        self.lonMaxLineEdit = QtWidgets.QLineEdit(self)
        self.lonMaxLineEdit.setText(str(ConfigFile.settings["fL0LonMax"]))
        self.lonMaxLineEdit.setValidator(doubleValidator)

        directionLabel = QtWidgets.QLabel("Ferry Direction", self)
        self.directionComboBox = QtWidgets.QComboBox(self)
        self.directionComboBox.addItem("")
        self.directionComboBox.addItem("E")
        self.directionComboBox.addItem("W")
        index = self.directionComboBox.findText(str(ConfigFile.settings["cL0Direction"]))
        self.directionComboBox.setCurrentIndex(index)

        l0PerformCleaningLabel = QtWidgets.QLabel("SAS Solar Tracker - Angle Detection/Cleaning", self)
        self.l0PerformCleaningCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL0PerformCleaning"]) == 1:
            self.l0PerformCleaningCheckBox.setChecked(True)

        l0AngleMinLabel = QtWidgets.QLabel("Angle Min", self)
        self.l0AngleMinLineEdit = QtWidgets.QLineEdit(self)
        self.l0AngleMinLineEdit.setText(str(ConfigFile.settings["fL0AngleMin"]))
        self.l0AngleMinLineEdit.setValidator(doubleValidator)

        l0AngleMaxLabel = QtWidgets.QLabel("Angle Max", self)
        self.l0AngleMaxLineEdit = QtWidgets.QLineEdit(self)
        self.l0AngleMaxLineEdit.setText(str(ConfigFile.settings["fL0AngleMax"]))
        self.l0AngleMaxLineEdit.setValidator(doubleValidator)

        l0RotatorAngleMinLabel = QtWidgets.QLabel("Rotator Angle Min", self)
        self.l0RotatorAngleMinLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorAngleMinLineEdit.setText(str(ConfigFile.settings["fL0RotatorAngleMin"]))
        self.l0RotatorAngleMinLineEdit.setValidator(doubleValidator)

        l0RotatorAngleMaxLabel = QtWidgets.QLabel("Rotator Angle Max", self)
        self.l0RotatorAngleMaxLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorAngleMaxLineEdit.setText(str(ConfigFile.settings["fL0RotatorAngleMax"]))
        self.l0RotatorAngleMaxLineEdit.setValidator(doubleValidator)

        l0RotatorHomeAngleLabel = QtWidgets.QLabel("Home Angle", self)
        self.l0RotatorHomeAngleLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorHomeAngleLineEdit.setText(str(ConfigFile.settings["fL0RotatorHomeAngle"]))
        self.l0RotatorHomeAngleLineEdit.setValidator(doubleValidator)
        
        l0RotatorDelayLabel = QtWidgets.QLabel("Rotator Delay (Seconds)", self)
        self.l0RotatorDelayLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorDelayLineEdit.setText(str(ConfigFile.settings["fL0RotatorDelay"]))
        self.l0RotatorDelayLineEdit.setValidator(doubleValidator)



        l3InterpIntervalLabel = QtWidgets.QLabel("Level 3 - Interpolation Interval (nm)", self)
        self.l3InterpIntervalLineEdit = QtWidgets.QLineEdit(self)
        self.l3InterpIntervalLineEdit.setText(str(ConfigFile.settings["fL3aInterpInterval"]))
        self.l3InterpIntervalLineEdit.setValidator(doubleValidator)


        l4QualityFlagLabel = QtWidgets.QLabel("Level 4 - Enable Meteorological Flags", self)
        self.l4QualityFlagCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL4EnableQualityFlags"]) == 1:
            self.l4QualityFlagCheckBox.setChecked(True)

        l4EsFlagLabel = QtWidgets.QLabel("Es Flag", self)
        self.l4EsFlagLineEdit = QtWidgets.QLineEdit("", self)
        self.l4EsFlagLineEdit.setText(str(ConfigFile.settings["fL4SignificantEsFlag"]))
        self.l4EsFlagLineEdit.setValidator(doubleValidator)

        l4DawnDuskFlagLabel = QtWidgets.QLabel("Dawn/Dusk Flag", self)
        self.l4DawnDuskFlagLineEdit = QtWidgets.QLineEdit("", self)
        self.l4DawnDuskFlagLineEdit.setText(str(ConfigFile.settings["fL4DawnDuskFlag"]))
        self.l4DawnDuskFlagLineEdit.setValidator(doubleValidator)

        l4RainfallHumidityFlagLabel = QtWidgets.QLabel("Rainfall/Humidity Flag", self)
        self.l4RainfallHumidityFlagLineEdit = QtWidgets.QLineEdit("", self)
        self.l4RainfallHumidityFlagLineEdit.setText(str(ConfigFile.settings["fL4RainfallHumidityFlag"]))
        self.l4RainfallHumidityFlagLineEdit.setValidator(doubleValidator)

        l4TimeIntervalLabel = QtWidgets.QLabel("Level 4 - Rrs Time Interval (seconds)", self)
        self.l4TimeIntervalLineEdit = QtWidgets.QLineEdit(self)
        self.l4TimeIntervalLineEdit.setText(str(ConfigFile.settings["fL4TimeInterval"]))
        self.l4TimeIntervalLineEdit.setValidator(intValidator)

        l4DefaultWindSpeedLabel = QtWidgets.QLabel("Level 4 - Default Wind Speed (m/s)", self)
        self.l4DefaultWindSpeedLineEdit = QtWidgets.QLineEdit(self)
        self.l4DefaultWindSpeedLineEdit.setText(str(ConfigFile.settings["fL4DefaultWindSpeed"]))
        self.l4DefaultWindSpeedLineEdit.setValidator(doubleValidator)

        #l4NIRCorrectionLabel = QtWidgets.QLabel("Level 4 - Enable Near-infrared Correction", self)
        #self.l4NIRCorrectionCheckBox = QtWidgets.QCheckBox("", self)
        #if int(ConfigFile.settings["bL4PerformNIRCorrection"]) == 1:
        #    self.l4NIRCorrectionCheckBox.setChecked(True)


        self.saveButton = QtWidgets.QPushButton("Save")
        self.cancelButton = QtWidgets.QPushButton("Cancel")

        self.saveButton.clicked.connect(self.saveButtonPressed)
        self.cancelButton.clicked.connect(self.cancelButtonPressed)


        print("ConfigWindow - Create Layout")

        vBox = QtWidgets.QVBoxLayout()
        vBox.addWidget(self.nameLabel)
        vBox.addSpacing(10)


        vBox1 = QtWidgets.QVBoxLayout()

        #vBox.addStretch(1)
        vBox1.addWidget(self.addCalibrationFileButton)
        vBox1.addWidget(self.calibrationFileComboBox)
        vBox1.addWidget(self.calibrationEnabledCheckBox)
        vBox1.addWidget(calibrationFrameTypeLabel)
        vBox1.addWidget(self.calibrationFrameTypeComboBox)
        vBox1.addSpacing(25)


        #vBox1 = QtWidgets.QVBoxLayout()

        #vBox = QtWidgets.QVBoxLayout()
        #vBox.addStretch(1)
        vBox1.addWidget(l0CheckCoordsLabel)
        vBox1.addWidget(self.l0CheckCoordsCheckBox)
        vBox1.addWidget(lonMinLabel)
        vBox1.addWidget(self.lonMinLineEdit)
        vBox1.addWidget(lonMaxLabel)
        vBox1.addWidget(self.lonMaxLineEdit)
        vBox1.addWidget(directionLabel)
        vBox1.addWidget(self.directionComboBox)

        vBox1.addWidget(l0PerformCleaningLabel)
        vBox1.addWidget(self.l0PerformCleaningCheckBox)
        vBox1.addWidget(l0AngleMinLabel)
        vBox1.addWidget(self.l0AngleMinLineEdit)
        vBox1.addWidget(l0AngleMaxLabel)
        vBox1.addWidget(self.l0AngleMaxLineEdit)
        vBox1.addWidget(l0RotatorAngleMinLabel)
        vBox1.addWidget(self.l0RotatorAngleMinLineEdit)
        vBox1.addWidget(l0RotatorAngleMaxLabel)
        vBox1.addWidget(self.l0RotatorAngleMaxLineEdit)
        vBox1.addWidget(l0RotatorHomeAngleLabel)
        vBox1.addWidget(self.l0RotatorHomeAngleLineEdit)
        vBox1.addWidget(l0RotatorDelayLabel)
        vBox1.addWidget(self.l0RotatorDelayLineEdit)


        vBox2 = QtWidgets.QVBoxLayout()
        vBox2.setAlignment(QtCore.Qt.AlignBottom)

        vBox2.addWidget(l3InterpIntervalLabel)
        vBox2.addWidget(self.l3InterpIntervalLineEdit)


        vBox2.addWidget(l4QualityFlagLabel)
        vBox2.addWidget(self.l4QualityFlagCheckBox)
        vBox2.addWidget(l4EsFlagLabel)
        vBox2.addWidget(self.l4EsFlagLineEdit)
        vBox2.addWidget(l4DawnDuskFlagLabel)
        vBox2.addWidget(self.l4DawnDuskFlagLineEdit)
        vBox2.addWidget(l4RainfallHumidityFlagLabel)
        vBox2.addWidget(self.l4RainfallHumidityFlagLineEdit)

        vBox2.addWidget(l4TimeIntervalLabel)
        vBox2.addWidget(self.l4TimeIntervalLineEdit)
        vBox2.addWidget(l4DefaultWindSpeedLabel)
        vBox2.addWidget(self.l4DefaultWindSpeedLineEdit)
        #vBox2.addWidget(l4NIRCorrectionLabel)
        #vBox2.addWidget(self.l4NIRCorrectionCheckBox)
        vBox2.addSpacing(25)
        
        hBox = QtWidgets.QHBoxLayout()
        hBox.addLayout(vBox1)
        hBox.addSpacing(50)
        hBox.addLayout(vBox2)        


        saveHBox = QtWidgets.QHBoxLayout()
        saveHBox.addStretch(1)
        saveHBox.addWidget(self.saveButton)
        saveHBox.addWidget(self.cancelButton)


        vBox.addLayout(hBox)
        vBox.addLayout(saveHBox)


        self.setLayout(vBox)

        self.setGeometry(300, 300, 400, 750)
        self.setWindowTitle('Edit Config')
        #self.show()
        print("ConfigWindow - initUI Done")


    def addCalibrationFileButtonPressed(self):
        print("CalibrationEditWindow - Add Calibration File Pressed")
        fnames = QtWidgets.QFileDialog.getOpenFileNames(self, "Add Calibration Files")
        print(fnames)

        configName = self.name
        calibrationDir = os.path.splitext(configName)[0] + "_Calibration"
        configPath = os.path.join("Config", calibrationDir)
        for src in fnames[0]:
            (dirpath, filename) = os.path.split(src)
            dest = os.path.join(configPath, filename)
            print(src)
            print(dest)
            shutil.copy(src, dest)
        #print(fp)


    def getCalibrationSettings(self):
        print("CalibrationEditWindow - getCalibrationSettings")
        ConfigFile.refreshCalibrationFiles()
        calFileName = self.calibrationFileComboBox.currentText()
        calConfig = ConfigFile.getCalibrationConfig(calFileName)
        #print(calConfig["enabled"])
        #print(calConfig["frameType"])
        self.calibrationEnabledCheckBox.blockSignals(True)
        self.calibrationFrameTypeComboBox.blockSignals(True)

        self.calibrationEnabledCheckBox.setChecked(bool(calConfig["enabled"]))
        index = self.calibrationFrameTypeComboBox.findText(str(calConfig["frameType"]))
        self.calibrationFrameTypeComboBox.setCurrentIndex(index)

        self.calibrationEnabledCheckBox.blockSignals(False)
        self.calibrationFrameTypeComboBox.blockSignals(False)


    def setCalibrationSettings(self):
        print("CalibrationEditWindow - setCalibrationSettings")
        calFileName = self.calibrationFileComboBox.currentText()
        enabled = self.calibrationEnabledCheckBox.isChecked()
        frameType = self.calibrationFrameTypeComboBox.currentText()
        ConfigFile.setCalibrationConfig(calFileName, enabled, frameType)


    def calibrationFileChanged(self, i):
        print("CalibrationEditWindow - Calibration File Changed")
        print("Current index",i,"selection changed ", self.calibrationFileComboBox.currentText())
        calFileName = self.calibrationFileComboBox.currentText()
        calDir = ConfigFile.getCalibrationDirectory()
        calPath = os.path.join(calDir, calFileName)
        #print("calPath: " + calPath)
        if os.path.isfile(calPath):
            self.getCalibrationSettings()
            self.calibrationEnabledCheckBox.setEnabled(True)
            self.calibrationFrameTypeComboBox.setEnabled(True)
        else:
            self.calibrationEnabledCheckBox.setEnabled(False)
            self.calibrationFrameTypeComboBox.setEnabled(False)


    def calibrationEnabledStateChanged(self):
        print("CalibrationEditWindow - Calibration Enabled State Changed")
        print(self.calibrationEnabledCheckBox.isChecked())
        self.setCalibrationSettings()

    def calibrationFrameTypeChanged(self, i):
        print("CalibrationEditWindow - Calibration Frame Type Changed")
        print("Current index",i,"selection changed ", self.calibrationFrameTypeComboBox.currentText())
        self.setCalibrationSettings()


    def saveButtonPressed(self):
        print("ConfigWindow - Save Pressed")

        ConfigFile.settings["bL0CheckCoords"] = int(self.l0CheckCoordsCheckBox.isChecked())
        ConfigFile.settings["fL0LonMin"] = float(self.lonMinLineEdit.text())
        ConfigFile.settings["fL0LonMax"] = float(self.lonMaxLineEdit.text())
        ConfigFile.settings["cL0Direction"] = self.directionComboBox.currentText()
        ConfigFile.settings["bL0PerformCleaning"] = int(self.l0PerformCleaningCheckBox.isChecked())
        ConfigFile.settings["fL0AngleMin"] = float(self.l0AngleMinLineEdit.text())
        ConfigFile.settings["fL0AngleMax"] = float(self.l0AngleMaxLineEdit.text())
        ConfigFile.settings["fL0RotatorAngleMin"] = float(self.l0RotatorAngleMinLineEdit.text())
        ConfigFile.settings["fL0RotatorAngleMax"] = float(self.l0RotatorAngleMaxLineEdit.text())
        ConfigFile.settings["fL0RotatorHomeAngle"] = float(self.l0RotatorHomeAngleLineEdit.text())
        ConfigFile.settings["fL0RotatorDelay"] = float(self.l0RotatorDelayLineEdit.text())

        ConfigFile.settings["fL3aInterpInterval"] = float(self.l3InterpIntervalLineEdit.text())

        ConfigFile.settings["bL4EnableQualityFlags"] = int(self.l4QualityFlagCheckBox.isChecked())
        ConfigFile.settings["fL4SignificantEsFlag"] = float(self.l4EsFlagLineEdit.text())
        ConfigFile.settings["fL4DawnDuskFlag"] = float(self.l4DawnDuskFlagLineEdit.text())
        ConfigFile.settings["fL4RainfallHumidityFlag"] = float(self.l4RainfallHumidityFlagLineEdit.text())
        ConfigFile.settings["fL4TimeInterval"] = int(self.l4TimeIntervalLineEdit.text())
        ConfigFile.settings["fL4DefaultWindSpeed"] = float(self.l4DefaultWindSpeedLineEdit.text())
        #ConfigFile.settings["bL4PerformNIRCorrection"] = int(self.l4NIRCorrectionCheckBox.isChecked())

        ConfigFile.saveConfig(self.name)

        QtWidgets.QMessageBox.about(self, "Edit Config File", "Config File Saved")
        self.close()



    def cancelButtonPressed(self):
        print("ConfigWindow - Cancel Pressed")
        self.close()

