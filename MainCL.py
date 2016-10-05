
from Controller import Controller
from PreprocessRawFile import PreprocessRawFile


def main():
    #print("test:", float(b"+12.69"))
    calibrationMap = Controller.processCalibration("Calibration")
    #PreprocessRawFile.processDirectory("RawData", calibrationMap, 12317.307, 12356.5842, 'E')
    Controller.processDirectory("Data", calibrationMap)


if __name__ == "__main__":
    main()
