
from Controller import Controller
from PreprocessRawFile import PreprocessRawFile

from config import settings

def main():
    calibrationDirectory = settings["sCalibrationFolder"].strip('"')
    preprocessDirectory = settings["sPreprocessFolder"].strip('"')
    dataDirectory = settings["sProcessDataFolder"].strip('"')

    calibrationMap = Controller.processCalibration(calibrationDirectory)
    PreprocessRawFile.processDirectory(preprocessDirectory, calibrationMap)
    Controller.processDirectory(dataDirectory, calibrationMap, settings)


if __name__ == "__main__":
    main()
