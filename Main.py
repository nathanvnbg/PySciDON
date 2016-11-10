
import sys
from PyQt4 import QtCore, QtGui

from Controller import Controller
from config import settings


class Window(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        self.lStatus = QtGui.QLabel('Multi-Level Processing', self)
        self.lStatus.move(30, 20)


        self.bMulti1 = QtGui.QPushButton("Level 1 --> 2", self)
        self.bMulti1.move(30, 50)

        self.bMulti2 = QtGui.QPushButton("Level 1 --> 2s", self)
        self.bMulti2.move(30, 100)

        self.bMulti3 = QtGui.QPushButton("Level 1 --> 3a", self)
        self.bMulti3.move(30, 150)

        self.bMulti4 = QtGui.QPushButton("Level 1 --> 4", self)
        self.bMulti4.move(30, 200)


        '''
        self.lStatus = QtGui.QLabel('Single-Level Processing', self)
        self.lStatus.move(30, 270)


        self.bSingle0 = QtGui.QPushButton("Preprocess Raw", self)
        self.bSingle0.move(30, 300)

        self.bSingle1 = QtGui.QPushButton("Level 1 --> 1a", self)
        self.bSingle1.move(30, 350)

        self.bSingle2 = QtGui.QPushButton("Level 1a --> 1b", self)
        self.bSingle2.move(30, 400)

        self.bSingle3 = QtGui.QPushButton("Level 1b --> 2", self)
        self.bSingle3.move(30, 450)

        self.bSingle4 = QtGui.QPushButton("Level 2 --> 2s", self)
        self.bSingle4.move(30, 500)

        self.bSingle5 = QtGui.QPushButton("Level 2s --> 3a", self)
        self.bSingle5.move(30, 550)

        self.bSingle6 = QtGui.QPushButton("Level 3a --> 4", self)
        self.bSingle6.move(30, 600)
        '''

        self.bMulti1.clicked.connect(self.bMulti1Clicked)            
        self.bMulti2.clicked.connect(self.bMulti2Clicked)
        self.bMulti3.clicked.connect(self.bMulti3Clicked)            
        self.bMulti4.clicked.connect(self.bMulti4Clicked)

        '''
        self.bSingle0.clicked.connect(self.buttonClicked)
        self.bSingle1.clicked.connect(self.buttonClicked)            
        self.bSingle2.clicked.connect(self.buttonClicked)
        self.bSingle3.clicked.connect(self.buttonClicked)            
        self.bSingle4.clicked.connect(self.buttonClicked)
        self.bSingle5.clicked.connect(self.buttonClicked)            
        self.bSingle6.clicked.connect(self.buttonClicked)
        '''

        self.setGeometry(300, 300, 290, 700)
        self.setWindowTitle('Test')
        self.show()

    def processMulti(self, level):
        print("Process Multi-Level")
        calibrationDirectory = settings["sCalibrationFolder"].strip('"')
        preprocessDirectory = settings["sPreprocessFolder"].strip('"')
        dataDirectory = settings["sProcessDataFolder"].strip('"')

        print("Process Calibration Files")
        calibrationMap = Controller.processCalibration(calibrationDirectory)
        print("Preprocess Raw Files")
        startLongitude = float(settings["fL0LonMin"])
        endLongitude = float(settings["fL0LonMax"])
        direction = settings["cL0Direction"].strip("'")
        #print(startLongitude, endLongitude, direction)
        Controller.preprocessData(preprocessDirectory, calibrationMap, startLongitude, endLongitude, direction)
        print("Process Raw Files")
        Controller.processDirectory(dataDirectory, calibrationMap, level)  

    def bMulti1Clicked(self):
        self.processMulti(1)

    def bMulti2Clicked(self):
        self.processMulti(2)

    def bMulti3Clicked(self):
        self.processMulti(3)

    def bMulti4Clicked(self):
        self.processMulti(4)


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
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
