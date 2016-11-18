
from Controller import Controller
from PreprocessRawFile import PreprocessRawFile

from config import settings

def main():
    calibrationDirectory = settings["sCalibrationFolder"].strip('"')
    preprocessDirectory = settings["sPreprocessFolder"].strip('"')
    dataDirectory = settings["sProcessDataFolder"].strip('"')

    startLongitude = float(settings["fL0LonMin"])
    endLongitude = float(settings["fL0LonMax"])
    direction = settings["cL0Direction"].strip("'")
    #print(startLongitude, endLongitude, direction)

    calibrationMap = Controller.processCalibration(calibrationDirectory)
    #Controller.preprocessData(preprocessDirectory, dataDirectory, calibrationMap, startLongitude, endLongitude, direction)
    Controller.processDirectory(dataDirectory, calibrationMap)


if __name__ == "__main__":
    main()
