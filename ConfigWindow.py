
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

        l0Label = QtWidgets.QLabel("Level 0 - Preprocessing", self)
        l3Label = QtWidgets.QLabel("Level 3a - Wavelength Interpolation", self)
        l4Label = QtWidgets.QLabel("Level 4 - Rrs Calculation", self)


        l0CheckCoordsLabel = QtWidgets.QLabel("Enable Longitude/Direction Checking", self)
        self.l0CheckCoordsCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL0CheckCoords"]) == 1:
            self.l0CheckCoordsCheckBox.setChecked(True)

        self.lonMinLabel = QtWidgets.QLabel("Longitude Min", self)
        self.lonMinLineEdit = QtWidgets.QLineEdit(self)
        self.lonMinLineEdit.setText(str(ConfigFile.settings["fL0LonMin"]))
        self.lonMinLineEdit.setValidator(doubleValidator)

        self.lonMaxLabel = QtWidgets.QLabel("Longitude Max", self)
        self.lonMaxLineEdit = QtWidgets.QLineEdit(self)
        self.lonMaxLineEdit.setText(str(ConfigFile.settings["fL0LonMax"]))
        self.lonMaxLineEdit.setValidator(doubleValidator)

        self.directionLabel = QtWidgets.QLabel("Ferry Direction", self)
        self.directionComboBox = QtWidgets.QComboBox(self)
        self.directionComboBox.addItem("")
        self.directionComboBox.addItem("E")
        self.directionComboBox.addItem("W")
        index = self.directionComboBox.findText(str(ConfigFile.settings["cL0Direction"]))
        self.directionComboBox.setCurrentIndex(index)

        self.l0CheckCoordsCheckBoxUpdate()



        l0CleanRotatorAngleLabel = QtWidgets.QLabel("SAS Solar Tracker - Rotator Angle Cleaning", self)
        self.l0CleanRotatorAngleCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL0CleanRotatorAngle"]) == 1:
            self.l0CleanRotatorAngleCheckBox.setChecked(True)

        self.l0RotatorAngleMinLabel = QtWidgets.QLabel("Rotator Angle Min", self)
        self.l0RotatorAngleMinLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorAngleMinLineEdit.setText(str(ConfigFile.settings["fL0RotatorAngleMin"]))
        self.l0RotatorAngleMinLineEdit.setValidator(doubleValidator)

        self.l0RotatorAngleMaxLabel = QtWidgets.QLabel("Rotator Angle Max", self)
        self.l0RotatorAngleMaxLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorAngleMaxLineEdit.setText(str(ConfigFile.settings["fL0RotatorAngleMax"]))
        self.l0RotatorAngleMaxLineEdit.setValidator(doubleValidator)

        self.l0RotatorDelayLabel = QtWidgets.QLabel("Rotator Delay (Seconds)", self)
        self.l0RotatorDelayLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorDelayLineEdit.setText(str(ConfigFile.settings["fL0RotatorDelay"]))
        self.l0RotatorDelayLineEdit.setValidator(doubleValidator)

        self.l0CleanRotatorAngleCheckBoxUpdate()


        l0CleanSunAngleLabel = QtWidgets.QLabel("SAS Solar Tracker - Sun Angle Cleaning", self)
        self.l0CleanSunAngleCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL0CleanSunAngle"]) == 1:
            self.l0CleanSunAngleCheckBox.setChecked(True)

        self.l0SunAngleMinLabel = QtWidgets.QLabel("Sun Angle Min", self)
        self.l0SunAngleMinLineEdit = QtWidgets.QLineEdit(self)
        self.l0SunAngleMinLineEdit.setText(str(ConfigFile.settings["fL0SunAngleMin"]))
        self.l0SunAngleMinLineEdit.setValidator(doubleValidator)

        self.l0SunAngleMaxLabel = QtWidgets.QLabel("Sun Angle Max", self)
        self.l0SunAngleMaxLineEdit = QtWidgets.QLineEdit(self)
        self.l0SunAngleMaxLineEdit.setText(str(ConfigFile.settings["fL0SunAngleMax"]))
        self.l0SunAngleMaxLineEdit.setValidator(doubleValidator)

        self.l0RotatorHomeAngleLabel = QtWidgets.QLabel("Rotator Home Angle", self)
        self.l0RotatorHomeAngleLineEdit = QtWidgets.QLineEdit(self)
        self.l0RotatorHomeAngleLineEdit.setText(str(ConfigFile.settings["fL0RotatorHomeAngle"]))
        self.l0RotatorHomeAngleLineEdit.setValidator(doubleValidator)

        self.l0CleanSunAngleCheckBoxUpdate()


        l0SplitRawFileLabel = QtWidgets.QLabel("SAS Solar Tracker - Split Raw File", self)
        self.l0SplitRawFileCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL0SplitRawFile"]) == 1:
            self.l0SplitRawFileCheckBox.setChecked(True)



        l3InterpIntervalLabel = QtWidgets.QLabel("Interpolation Interval (nm)", self)
        self.l3InterpIntervalLineEdit = QtWidgets.QLineEdit(self)
        self.l3InterpIntervalLineEdit.setText(str(ConfigFile.settings["fL3aInterpInterval"]))
        self.l3InterpIntervalLineEdit.setValidator(doubleValidator)



        # Settings to determine how to calculate Rrs
        self.l4RrsCalculationTypeBox = QtWidgets.QGroupBox("L4 Rrs Calculation Type")

        self.l4MeanButton = QtWidgets.QRadioButton("Mean")
        self.l4MeanButton.setChecked(ConfigFile.settings["iL4CalculationType"] == 0)
        
        self.l4MedianButton = QtWidgets.QRadioButton("Median")
        self.l4MedianButton.setChecked(ConfigFile.settings["iL4CalculationType"] == 1)
        
        
        # Settings to determine how to split Rrs data
        self.l4SplitDataBox = QtWidgets.QGroupBox("Split L4 Data")

        self.l4TimeButton = QtWidgets.QRadioButton("Time (seconds)")
        self.l4TimeButton.setChecked(ConfigFile.settings["iL4SplitDataType"] == 0)
        self.l4TimeIntervalLineEdit = QtWidgets.QLineEdit(self)
        self.l4TimeIntervalLineEdit.setText(str(ConfigFile.settings["fL4TimeInterval"]))
        self.l4TimeIntervalLineEdit.setValidator(intValidator)
        
        self.l4LatitudeButton = QtWidgets.QRadioButton("Latitude")
        self.l4LatitudeButton.setChecked(ConfigFile.settings["iL4SplitDataType"] == 1)
        self.l4LatitudeStepLineEdit = QtWidgets.QLineEdit(self)
        self.l4LatitudeStepLineEdit.setText(str(ConfigFile.settings["fL4LatitudeStep"]))
        self.l4LatitudeStepLineEdit.setValidator(doubleValidator)
        
        self.l4LongitudeButton = QtWidgets.QRadioButton("Longitude")
        self.l4LongitudeButton.setChecked(ConfigFile.settings["iL4SplitDataType"] == 2)
        self.l4LongitudeStepLineEdit = QtWidgets.QLineEdit(self)
        self.l4LongitudeStepLineEdit.setText(str(ConfigFile.settings["fL4LongitudeStep"]))
        self.l4LongitudeStepLineEdit.setValidator(doubleValidator)
        
        self.l4SplitDataButtonUpdate()
        
        
        # Settings for Meteorologial flags
        l4QualityFlagLabel = QtWidgets.QLabel("Enable Meteorological Flags", self)
        self.l4QualityFlagCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL4EnableQualityFlags"]) == 1:
            self.l4QualityFlagCheckBox.setChecked(True)

        self.l4EsFlagLabel = QtWidgets.QLabel("Es Flag", self)
        self.l4EsFlagLineEdit = QtWidgets.QLineEdit("", self)
        self.l4EsFlagLineEdit.setText(str(ConfigFile.settings["fL4SignificantEsFlag"]))
        self.l4EsFlagLineEdit.setValidator(doubleValidator)

        self.l4DawnDuskFlagLabel = QtWidgets.QLabel("Dawn/Dusk Flag", self)
        self.l4DawnDuskFlagLineEdit = QtWidgets.QLineEdit("", self)
        self.l4DawnDuskFlagLineEdit.setText(str(ConfigFile.settings["fL4DawnDuskFlag"]))
        self.l4DawnDuskFlagLineEdit.setValidator(doubleValidator)

        self.l4RainfallHumidityFlagLabel = QtWidgets.QLabel("Rainfall/Humidity Flag", self)
        self.l4RainfallHumidityFlagLineEdit = QtWidgets.QLineEdit("", self)
        self.l4RainfallHumidityFlagLineEdit.setText(str(ConfigFile.settings["fL4RainfallHumidityFlag"]))
        self.l4RainfallHumidityFlagLineEdit.setValidator(doubleValidator)

        self.l4QualityFlagCheckBoxUpdate()


        l4RhoSkyLabel = QtWidgets.QLabel("Rho Sky", self)
        self.l4RhoSkyLineEdit = QtWidgets.QLineEdit(self)
        self.l4RhoSkyLineEdit.setText(str(ConfigFile.settings["fL4RhoSky"]))
        self.l4RhoSkyLineEdit.setValidator(doubleValidator)

        # Wind speed settings
        l4EnableWindSpeedCalculationLabel = QtWidgets.QLabel("Enable Wind Speed Calculation", self)
        self.l4EnableWindSpeedCalculationCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL4EnableWindSpeedCalculation"]) == 1:
            self.l4EnableWindSpeedCalculationCheckBox.setChecked(True)

        self.l4DefaultWindSpeedLabel = QtWidgets.QLabel("Default Wind Speed (m/s)", self)
        self.l4DefaultWindSpeedLineEdit = QtWidgets.QLineEdit(self)
        self.l4DefaultWindSpeedLineEdit.setText(str(ConfigFile.settings["fL4DefaultWindSpeed"]))
        self.l4DefaultWindSpeedLineEdit.setValidator(doubleValidator)
        
        self.l4EnableWindSpeedCalculationCheckBoxUpdate()
        

        l4NIRCorrectionLabel = QtWidgets.QLabel("Enable Near-infrared Correction", self)
        self.l4NIRCorrectionCheckBox = QtWidgets.QCheckBox("", self)
        if int(ConfigFile.settings["bL4PerformNIRCorrection"]) == 1:
            self.l4NIRCorrectionCheckBox.setChecked(True)
            
        # Ship noise value to subtract from Rrs
        l4ShipNoiseCorrectionLabel = QtWidgets.QLabel("Ship Noise (Subtract from Rrs)", self)
        self.l4ShipNoiseCorrectionLineEdit = QtWidgets.QLineEdit(self)
        self.l4ShipNoiseCorrectionLineEdit.setText(str(ConfigFile.settings["fL4ShipNoiseCorrection"]))
        self.l4ShipNoiseCorrectionLineEdit.setValidator(doubleValidator)

        #l4EnablePercentLtLabel = QtWidgets.QLabel("Level 4 - Enable Percent Lt Calculation", self)
        #self.l4EnablePercentLtCheckBox = QtWidgets.QCheckBox("", self)
        #if int(ConfigFile.settings["bL4EnablePercentLtCorrection"]) == 1:
        #    self.l4EnablePercentLtCheckBox.setChecked(True)

        # Set percentage for Rrs calculation
        l4PercentLtLabel = QtWidgets.QLabel("Percent Lt", self)
        self.l4PercentLtLineEdit = QtWidgets.QLineEdit(self)
        self.l4PercentLtLineEdit.setText(str(ConfigFile.settings["fL4PercentLt"]))
        self.l4PercentLtLineEdit.setValidator(doubleValidator)

        # Wavelength used for Rrs calculation
        l4PercentLtWavelengthLabel = QtWidgets.QLabel("Percent Lt Wavelength", self)
        self.l4PercentLtWavelengthLineEdit = QtWidgets.QLineEdit(self)
        self.l4PercentLtWavelengthLineEdit.setText(str(ConfigFile.settings["fL4PercentLtWavelength"]))
        self.l4PercentLtWavelengthLineEdit.setValidator(doubleValidator)


        self.saveButton = QtWidgets.QPushButton("Save")
        self.cancelButton = QtWidgets.QPushButton("Cancel")


        self.l0CheckCoordsCheckBox.clicked.connect(self.l0CheckCoordsCheckBoxUpdate)
        self.l0CleanRotatorAngleCheckBox.clicked.connect(self.l0CleanRotatorAngleCheckBoxUpdate)
        self.l0CleanSunAngleCheckBox.clicked.connect(self.l0CleanSunAngleCheckBoxUpdate)
        self.l4TimeButton.clicked.connect(self.l4SplitDataButtonUpdate)
        self.l4LatitudeButton.clicked.connect(self.l4SplitDataButtonUpdate)
        self.l4LongitudeButton.clicked.connect(self.l4SplitDataButtonUpdate)
        self.l4QualityFlagCheckBox.clicked.connect(self.l4QualityFlagCheckBoxUpdate)
        self.l4EnableWindSpeedCalculationCheckBox.clicked.connect(self.l4EnableWindSpeedCalculationCheckBoxUpdate)
            
        self.saveButton.clicked.connect(self.saveButtonPressed)
        self.cancelButton.clicked.connect(self.cancelButtonPressed)


        print("ConfigWindow - Create Layout")

        vBox = QtWidgets.QVBoxLayout()
        vBox.addWidget(self.nameLabel)
        vBox.addSpacing(10)


        vBox0 = QtWidgets.QVBoxLayout()

        vBox0.addWidget(self.addCalibrationFileButton)
        vBox0.addWidget(self.calibrationFileComboBox)
        vBox0.addWidget(self.calibrationEnabledCheckBox)
        vBox0.addWidget(calibrationFrameTypeLabel)
        vBox0.addWidget(self.calibrationFrameTypeComboBox)
        vBox0.addStretch(1)


        vBox1 = QtWidgets.QVBoxLayout()
        #vBox1.addSpacing(25)

        vBox1.addWidget(l0Label)
        vBox1.addWidget(l0CheckCoordsLabel)
        vBox1.addWidget(self.l0CheckCoordsCheckBox)
        vBox1.addWidget(self.lonMinLabel)
        vBox1.addWidget(self.lonMinLineEdit)
        vBox1.addWidget(self.lonMaxLabel)
        vBox1.addWidget(self.lonMaxLineEdit)
        vBox1.addWidget(self.directionLabel)
        vBox1.addWidget(self.directionComboBox)


        vBox1.addWidget(l0CleanRotatorAngleLabel)
        vBox1.addWidget(self.l0CleanRotatorAngleCheckBox)
        vBox1.addWidget(self.l0RotatorAngleMinLabel)
        vBox1.addWidget(self.l0RotatorAngleMinLineEdit)
        vBox1.addWidget(self.l0RotatorAngleMaxLabel)
        vBox1.addWidget(self.l0RotatorAngleMaxLineEdit)
        vBox1.addWidget(self.l0RotatorDelayLabel)
        vBox1.addWidget(self.l0RotatorDelayLineEdit)

        vBox1.addWidget(l0CleanSunAngleLabel)
        vBox1.addWidget(self.l0CleanSunAngleCheckBox)
        vBox1.addWidget(self.l0SunAngleMinLabel)
        vBox1.addWidget(self.l0SunAngleMinLineEdit)
        vBox1.addWidget(self.l0SunAngleMaxLabel)
        vBox1.addWidget(self.l0SunAngleMaxLineEdit)
        vBox1.addWidget(self.l0RotatorHomeAngleLabel)
        vBox1.addWidget(self.l0RotatorHomeAngleLineEdit)

        vBox1.addWidget(l0SplitRawFileLabel)
        vBox1.addWidget(self.l0SplitRawFileCheckBox)


        vBox2 = QtWidgets.QVBoxLayout()
        vBox2.setAlignment(QtCore.Qt.AlignTop)
        #vBox2.setAlignment(QtCore.Qt.AlignBottom)
                

        vBox2.addWidget(l3Label)
        vBox2.addWidget(l3InterpIntervalLabel)
        vBox2.addWidget(self.l3InterpIntervalLineEdit)

        vBox2.addSpacing(50)



        vBoxRrsCalculationType = QtWidgets.QVBoxLayout()

        vBoxRrsCalculationType.addWidget(self.l4MeanButton)
        vBoxRrsCalculationType.addWidget(self.l4MedianButton)
        
        self.l4RrsCalculationTypeBox.setLayout(vBoxRrsCalculationType)
        vBox2.addWidget(self.l4RrsCalculationTypeBox)
        
        vBox2.addSpacing(25)
        
        
        vBoxSplitData = QtWidgets.QVBoxLayout()

        vBoxSplitData.addWidget(self.l4TimeButton)
        vBoxSplitData.addWidget(self.l4TimeIntervalLineEdit)
        vBoxSplitData.addWidget(self.l4LatitudeButton)
        vBoxSplitData.addWidget(self.l4LatitudeStepLineEdit)
        vBoxSplitData.addWidget(self.l4LongitudeButton)
        vBoxSplitData.addWidget(self.l4LongitudeStepLineEdit)
        
        self.l4SplitDataBox.setLayout(vBoxSplitData)
        vBox2.addWidget(self.l4SplitDataBox)
        
        vBox2.addSpacing(25)


        vBox3 = QtWidgets.QVBoxLayout()
        vBox3.setAlignment(QtCore.Qt.AlignTop)
        #vBox3.setAlignment(QtCore.Qt.AlignBottom)
        
        vBox3.addWidget(l4Label)
        vBox3.addWidget(l4QualityFlagLabel)
        vBox3.addWidget(self.l4QualityFlagCheckBox)
        vBox3.addWidget(self.l4EsFlagLabel)
        vBox3.addWidget(self.l4EsFlagLineEdit)
        vBox3.addWidget(self.l4DawnDuskFlagLabel)
        vBox3.addWidget(self.l4DawnDuskFlagLineEdit)
        vBox3.addWidget(self.l4RainfallHumidityFlagLabel)
        vBox3.addWidget(self.l4RainfallHumidityFlagLineEdit)

        vBox3.addSpacing(25)

        vBox3.addWidget(l4RhoSkyLabel)
        vBox3.addWidget(self.l4RhoSkyLineEdit)
        vBox3.addWidget(l4EnableWindSpeedCalculationLabel)
        vBox3.addWidget(self.l4EnableWindSpeedCalculationCheckBox)        
        vBox3.addWidget(self.l4DefaultWindSpeedLabel)
        vBox3.addWidget(self.l4DefaultWindSpeedLineEdit)
        vBox3.addWidget(l4NIRCorrectionLabel)
        vBox3.addWidget(self.l4NIRCorrectionCheckBox)
        vBox3.addWidget(l4ShipNoiseCorrectionLabel)
        vBox3.addWidget(self.l4ShipNoiseCorrectionLineEdit)
        #vBox3.addWidget(l4EnablePercentLtLabel)
        #vBox3.addWidget(self.l4EnablePercentLtCheckBox)
        vBox3.addWidget(l4PercentLtLabel)
        vBox3.addWidget(self.l4PercentLtLineEdit)
        vBox3.addWidget(l4PercentLtWavelengthLabel)
        vBox3.addWidget(self.l4PercentLtWavelengthLineEdit)
        vBox3.addSpacing(25)
        
        
        hBox = QtWidgets.QHBoxLayout()
        hBox.addLayout(vBox0, 2)
        hBox.addSpacing(50)
        hBox.addLayout(vBox1)
        hBox.addSpacing(50)
        hBox.addLayout(vBox2)        
        hBox.addSpacing(50)
        hBox.addLayout(vBox3)      


        saveHBox = QtWidgets.QHBoxLayout()
        saveHBox.addStretch(1)
        saveHBox.addWidget(self.saveButton)
        saveHBox.addWidget(self.cancelButton)


        vBox.addLayout(hBox)
        vBox.addLayout(saveHBox)


        self.setLayout(vBox)

        self.setGeometry(300, 200, 700, 700)
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


    def l0CheckCoordsCheckBoxUpdate(self):
        print("ConfigWindow - l0CheckCoordsCheckBoxUpdate")

        disabled = (not self.l0CheckCoordsCheckBox.isChecked())
        self.lonMinLabel.setDisabled(disabled)
        self.lonMinLineEdit.setDisabled(disabled)
        self.lonMaxLabel.setDisabled(disabled)
        self.lonMaxLineEdit.setDisabled(disabled)
        self.directionLabel.setDisabled(disabled)
        self.directionComboBox.setDisabled(disabled)

    def l0CleanRotatorAngleCheckBoxUpdate(self):
        print("ConfigWindow - l0CleanRotatorAngleCheckBoxUpdate")
        
        disabled = (not self.l0CleanRotatorAngleCheckBox.isChecked())
        self.l0RotatorAngleMinLabel.setDisabled(disabled)
        self.l0RotatorAngleMinLineEdit.setDisabled(disabled)
        self.l0RotatorAngleMaxLabel.setDisabled(disabled)
        self.l0RotatorAngleMaxLineEdit.setDisabled(disabled)
        self.l0RotatorDelayLabel.setDisabled(disabled)
        self.l0RotatorDelayLineEdit.setDisabled(disabled)

    def l0CleanSunAngleCheckBoxUpdate(self):
        print("ConfigWindow - l0CleanSunAngleCheckBoxUpdate")
        
        disabled = (not self.l0CleanSunAngleCheckBox.isChecked())
        self.l0SunAngleMinLabel.setDisabled(disabled)
        self.l0SunAngleMinLineEdit.setDisabled(disabled)
        self.l0SunAngleMaxLabel.setDisabled(disabled)
        self.l0SunAngleMaxLineEdit.setDisabled(disabled)
        self.l0RotatorHomeAngleLabel.setDisabled(disabled)
        self.l0RotatorHomeAngleLineEdit.setDisabled(disabled)

    def l4SplitDataButtonUpdate(self):
        print("ConfigWindow - l4SplitDataButtonUpdate")
        
        disabled = (not self.l4TimeButton.isChecked())
        #self.l4TimeIntervalLabel.setDisabled(disabled)
        self.l4TimeIntervalLineEdit.setDisabled(disabled)
        disabled = (not self.l4LatitudeButton.isChecked())
        self.l4LatitudeStepLineEdit.setDisabled(disabled)
        disabled = (not self.l4LongitudeButton.isChecked())
        self.l4LongitudeStepLineEdit.setDisabled(disabled)

    def l4QualityFlagCheckBoxUpdate(self):
        print("ConfigWindow - l4QualityFlagCheckBoxUpdate")
        
        disabled = (not self.l4QualityFlagCheckBox.isChecked())
        self.l4EsFlagLabel.setDisabled(disabled)
        self.l4EsFlagLineEdit.setDisabled(disabled)
        self.l4DawnDuskFlagLabel.setDisabled(disabled)
        self.l4DawnDuskFlagLineEdit.setDisabled(disabled)
        self.l4RainfallHumidityFlagLabel.setDisabled(disabled)
        self.l4RainfallHumidityFlagLineEdit.setDisabled(disabled)

    def l4EnableWindSpeedCalculationCheckBoxUpdate(self):
        print("ConfigWindow - l4EnableWindSpeedCalculationCheckBoxUpdate")
        
        disabled = (not self.l4EnableWindSpeedCalculationCheckBox.isChecked())
        self.l4DefaultWindSpeedLabel.setDisabled(disabled)
        self.l4DefaultWindSpeedLineEdit.setDisabled(disabled)


    def saveButtonPressed(self):
        print("ConfigWindow - Save Pressed")

        ConfigFile.settings["bL0CheckCoords"] = int(self.l0CheckCoordsCheckBox.isChecked())
        ConfigFile.settings["fL0LonMin"] = float(self.lonMinLineEdit.text())
        ConfigFile.settings["fL0LonMax"] = float(self.lonMaxLineEdit.text())
        ConfigFile.settings["cL0Direction"] = self.directionComboBox.currentText()
        ConfigFile.settings["bL0CleanSunAngle"] = int(self.l0CleanSunAngleCheckBox.isChecked())
        ConfigFile.settings["bL0CleanRotatorAngle"] = int(self.l0CleanRotatorAngleCheckBox.isChecked())
        ConfigFile.settings["fL0SunAngleMin"] = float(self.l0SunAngleMinLineEdit.text())
        ConfigFile.settings["fL0SunAngleMax"] = float(self.l0SunAngleMaxLineEdit.text())
        ConfigFile.settings["fL0RotatorAngleMin"] = float(self.l0RotatorAngleMinLineEdit.text())
        ConfigFile.settings["fL0RotatorAngleMax"] = float(self.l0RotatorAngleMaxLineEdit.text())
        ConfigFile.settings["fL0RotatorHomeAngle"] = float(self.l0RotatorHomeAngleLineEdit.text())
        ConfigFile.settings["fL0RotatorDelay"] = float(self.l0RotatorDelayLineEdit.text())
        ConfigFile.settings["bL0SplitRawFile"] = int(self.l0SplitRawFileCheckBox.isChecked())

        ConfigFile.settings["fL3aInterpInterval"] = float(self.l3InterpIntervalLineEdit.text())


        if self.l4MeanButton.isChecked():
            ConfigFile.settings["iL4CalculationType"] = 0
        elif self.l4MedianButton.isChecked():
            ConfigFile.settings["iL4CalculationType"] = 1
        
        if self.l4TimeButton.isChecked():
            ConfigFile.settings["iL4SplitDataType"] = 0
        elif self.l4LatitudeButton.isChecked():
            ConfigFile.settings["iL4SplitDataType"] = 1
        elif self.l4LongitudeButton.isChecked():
            ConfigFile.settings["iL4SplitDataType"] = 2
            
        ConfigFile.settings["fL4TimeInterval"] = int(self.l4TimeIntervalLineEdit.text())
        ConfigFile.settings["fL4LatitudeStep"] = float(self.l4LatitudeStepLineEdit.text())
        ConfigFile.settings["fL4LongitudeStep"] = float(self.l4LongitudeStepLineEdit.text())

        ConfigFile.settings["bL4EnableQualityFlags"] = int(self.l4QualityFlagCheckBox.isChecked())
        ConfigFile.settings["fL4SignificantEsFlag"] = float(self.l4EsFlagLineEdit.text())
        ConfigFile.settings["fL4DawnDuskFlag"] = float(self.l4DawnDuskFlagLineEdit.text())
        ConfigFile.settings["fL4RainfallHumidityFlag"] = float(self.l4RainfallHumidityFlagLineEdit.text())
        ConfigFile.settings["fL4RhoSky"] = float(self.l4RhoSkyLineEdit.text())
        ConfigFile.settings["bL4EnableWindSpeedCalculation"] = int(self.l4EnableWindSpeedCalculationCheckBox.isChecked())
        ConfigFile.settings["fL4DefaultWindSpeed"] = float(self.l4DefaultWindSpeedLineEdit.text())
        ConfigFile.settings["bL4PerformNIRCorrection"] = int(self.l4NIRCorrectionCheckBox.isChecked())
        ConfigFile.settings["fL4ShipNoiseCorrection"] = float(self.l4ShipNoiseCorrectionLineEdit.text())
        #ConfigFile.settings["bL4EnablePercentLtCorrection"] = int(self.l4EnablePercentLtCheckBox.isChecked())
        ConfigFile.settings["fL4PercentLt"] = float(self.l4PercentLtLineEdit.text())
        ConfigFile.settings["fL4PercentLtWavelength"] = float(self.l4PercentLtWavelengthLineEdit.text())

        ConfigFile.saveConfig(self.name)

        QtWidgets.QMessageBox.about(self, "Edit Config File", "Config File Saved")
        self.close()



    def cancelButtonPressed(self):
        print("ConfigWindow - Cancel Pressed")
        self.close()

