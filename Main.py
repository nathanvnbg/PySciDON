
import sys
from PyQt4 import QtCore, QtGui


class Window(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        btn1 = QtGui.QPushButton("Button 1", self)
        btn1.move(30, 50)

        btn2 = QtGui.QPushButton("Button 2", self)
        btn2.move(150, 50)

        btn1.clicked.connect(self.buttonClicked)            
        btn2.clicked.connect(self.buttonClicked)

        self.lStatus = QtGui.QLabel('Status Label', self)
        self.lStatus.move(55, 80)  

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Event sender')
        self.show()

    def buttonClicked(self):
        sender = self.sender()
        self.lStatus.setText(sender.text() + ' was pressed')


	
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
