
from Controller import Controller


def main():
    #print("test:", float(b"+12.69"))
    calibrationMap = Controller.processCalibration("Calibration")
    Controller.processDirectory("Data", calibrationMap)


if __name__ == "__main__":
    main()
