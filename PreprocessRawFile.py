
import os
import sys
import time

from HDFDataset import HDFDataset
from HDFGroup import HDFGroup


class PreprocessRawFile:
    MAX_TAG_READ = 32
    MAX_BLOCK_READ = 1024
    SATHDR_READ = 128
    RESET_TAG_READ = MAX_TAG_READ-16
    
    # GPS:
    # Start 123 56.2 W
    # End 123 21.3 W

    # Converts date from integer
    @staticmethod
    def dateFromInt(d):
        s = str(int(d)).zfill(6)
        return time.strftime("%Y%m%d", time.strptime(s, "%d%m%y"))

    # Creates a raw file containing data within start/end longitude
    # Inputs:
    # gpGPSStart - Start GPS group
    # gpGPSEnd - End GPS Group
    # header - raw file header
    # messageStart - Start index of message in raw file
    # messageEnd - End index of message in raw file
    @staticmethod
    def createRawFile(dataDir, gpGPSStart, gpGPSEnd, direction, f, header, iStart, iEnd):
        # Determine filename from date/time
        startDate = str(int(gpGPSStart.getDataset("DATE").columns["NONE"][0]))
        endDate = str(int(gpGPSEnd.getDataset("DATE").columns["NONE"][0]))
        startTime = str(int(gpGPSStart.getDataset("UTCPOS").columns["NONE"][0])).zfill(6)
        endTime = str(int(gpGPSEnd.getDataset("UTCPOS").columns["NONE"][0])).zfill(6)

        # Reformate date
        startDate = PreprocessRawFile.dateFromInt(startDate)
        endDate = PreprocessRawFile.dateFromInt(endDate)

        # Determine direction
        lonStart = gpGPSStart.getDataset("LONPOS").columns["NONE"][0]
        lonEnd = gpGPSEnd.getDataset("LONPOS").columns["NONE"][0]
        course = 'W'
        if lonStart > lonEnd:
            course = 'E'

        if direction == course:
            # Copy block of messages between start and end
            pos = f.tell()
            f.seek(iStart)
            message = f.read(iEnd-iStart)
            f.seek(pos)

            filename = startDate + "T" + startTime + "_" + endDate + "T" + endTime + ".raw"
            print("Write:" + filename)

            # Write file
            data = header + message
            with open(os.path.join(dataDir, filename), 'wb') as fout:
                fout.write(data)
            #message = ""

    # Reads a raw file
    @staticmethod
    def processRawFile(filepath, dataDir, calibrationMap, startLongitude, endLongitude, direction):

        print("Read: " + filepath)

        # gpsState: set to 1 if within start/end longitude, else 0
        gpsState = 0

        # Saves the starting and ending GPS HDF Group
        gpGPSStart = None
        gpGPSEnd = None

        # Saves the raw file header
        header = b""
        #msg = b""
        #message = b""

        # Index of start/end message block for start/end longitude
        iStart = -1
        iEnd = -1

        #(dirpath, filename) = os.path.split(filepath)
        #print(filename)


        #posframe = 1

        # Note: Prosoft adds posframe=1 to the GPS for some reason
        #print(contextMap.keys())
        #gpsGroup = contextMap["$GPRMC"]
        #ds = gpsGroup.getDataset("POSFRAME")
        #ds.appendColumn(u"COUNT", posframe)
        #posframe += 1

        # Start reading raw binary file
        with open(filepath, 'rb') as f:
            while 1:
                # Reads a block of binary data from file
                pos = f.tell()
                b = f.read(PreprocessRawFile.MAX_TAG_READ)
                f.seek(pos)

                if not b:
                    break

                #print b
                # Search for frame tag string in block
                for i in range(0, PreprocessRawFile.MAX_TAG_READ):
                    testString = b[i:].upper()
                    #print("test: ", testString[:6])

                    # Reset file position on max read (frame tag not found)
                    if i == PreprocessRawFile.MAX_TAG_READ-1:
                        #f.read(PreprocessRawFile.MAX_TAG_READ)
                        f.read(PreprocessRawFile.RESET_TAG_READ)
                        break

                    # Reads header message type from frame tag
                    if testString.startswith(b"SATHDR"):
                        #print("SATHDR")
                        if i > 0:
                            f.read(i)
                        header += f.read(PreprocessRawFile.SATHDR_READ)

                        break
                    # Reads messages that starts with \$GPRMC and retrieves the CalibrationFile from map
                    else:
                        bytesRead = 0
                        for key in calibrationMap:
                            cf = calibrationMap[key]
                            if testString.startswith(b"$GPRMC") and testString.startswith(cf.id.upper().encode("utf-8")):
                                if i > 0:
                                    f.read(i)

                                # Read block from start of message
                                pos = f.tell()
                                msg = f.read(PreprocessRawFile.MAX_BLOCK_READ)
                                f.seek(pos)

                                # Convert message to HDFGroup
                                gp = HDFGroup()
                                bytesRead = cf.convertRaw(msg, gp)

                                # Read till end of message
                                if bytesRead >= 0:
                                    f.read(bytesRead)
                                    #if gpsState == 0:
                                    #    msg = f.read(bytesRead)
                                    #else:
                                    #    msg += f.read(bytesRead)


                                #gp.printd()
                                if gp.hasDataset("LONPOS"):
                                    #print("has gps")
                                    lonData = gp.getDataset("LONPOS")
                                    longitude = lonData.columns["NONE"][0]
                                    #print(longitude)
                                    # Detect if we are in specified longitude
                                    if longitude > startLongitude and longitude < endLongitude:
                                        if gpsState == 0:
                                            iStart = pos
                                            gpGPSStart = gp
                                        else:
                                            iEnd = f.tell()
                                            gpGPSEnd = gp
                                        #message += msg
                                        gpsState = 1
                                    # Not within start/end longitude
                                    else:
                                        if gpsState == 1:
                                            #print("Test")
                                            PreprocessRawFile.createRawFile(dataDir, gpGPSStart, gpGPSEnd, direction, f, header, iStart, iEnd)
                                        gpsState = 0

                                break
                        if bytesRead > 0:
                            break
            # In case file finished processing without reaching endLongitude
            if gpsState == 1:
                if gpGPSStart is not None and gpGPSEnd is not None:
                    PreprocessRawFile.createRawFile(dataDir, gpGPSStart, gpGPSEnd, direction, f, header, iStart, iEnd)

    @staticmethod
    def normalizeAngle(angle):
        x = angle % 360
        if x > 180:
            x =  abs(x - 360)
        return x


    # Remove data where
    # sun_azimuth - SAS_true != [90,135]
    @staticmethod
    def cleanRawFile(filepath, calibrationMap, angleMin, angleMax):
        print("Clean Raw File")

        header = b""
        message = b""

        # Index of start/end message block for start/end longitude
        iStart = 0
        iEnd = 0

        # Start reading raw binary file
        with open(filepath, 'rb') as f:
            while 1:
                # Reads a block of binary data from file
                pos = f.tell()
                b = f.read(PreprocessRawFile.MAX_TAG_READ)
                f.seek(pos)

                if not b:
                    break

                #print b
                # Search for frame tag string in block
                for i in range(0, PreprocessRawFile.MAX_TAG_READ):
                    testString = b[i:].upper()
                    #print("test: ", testString[:6])

                    # Reset file position on max read (frame tag not found)
                    if i == PreprocessRawFile.MAX_TAG_READ-1:
                        #f.read(PreprocessRawFile.MAX_TAG_READ)
                        f.read(PreprocessRawFile.RESET_TAG_READ)
                        break

                    # Reads header message type from frame tag
                    if testString.startswith(b"SATHDR"):
                        #print("SATHDR")
                        if i > 0:
                            f.read(i)
                        header += f.read(PreprocessRawFile.SATHDR_READ)

                        break
                    # Reads messages that starts with SATNAV and retrieves the CalibrationFile from map
                    else:
                        bytesRead = 0
                        for key in calibrationMap:
                            cf = calibrationMap[key]
                            if testString.startswith(b"SATNAV") and testString.startswith(cf.id.upper().encode("utf-8")):
                                if i > 0:
                                    f.read(i)

                                # Read block from start of message
                                pos = f.tell()
                                msg = f.read(PreprocessRawFile.MAX_BLOCK_READ)
                                f.seek(pos)

                                # Convert message to HDFGroup
                                gp = HDFGroup()
                                bytesRead = cf.convertRaw(msg, gp)

                                # Read till end of message
                                if bytesRead >= 0:
                                    f.read(bytesRead)


                                #gp.printd()
                                if gp.hasDataset("AZIMUTH") and gp.hasDataset("HEADING"):
                                    azimuthData = gp.getDataset("AZIMUTH")
                                    azimuth = azimuthData.columns["SUN"][0]

                                    sasTrueData = gp.getDataset("HEADING")
                                    sasTrue = sasTrueData.columns["SAS_TRUE"][0]

                                    #angle = (azimuth - sasTrue) % 360
                                    angle = PreprocessRawFile.normalizeAngle(azimuth - sasTrue)
                                    #print("Angle: ", angle)
                                    #if angle >= 90 and angle <= 135:
                                    if angle >= angleMin and angle <= angleMax:
                                        if iStart != -1:
                                            iEnd = f.tell()
    
                                            pos = f.tell()
                                            f.seek(iStart)
                                            msg = f.read(iEnd-iStart)
                                            f.seek(pos)
    
                                            message += msg
                                            iStart = f.tell()
                                        else:
                                            iStart = f.tell() - bytesRead
                                        
                                    else:
                                        print("Skip Bad Angle: ", angle)
                                        iStart = -1
                                        

                                break
                        if bytesRead > 0:
                            break
            if iStart != -1:
                f.seek(iStart)
                message += f.read()

        # Write file
        with open(filepath, 'wb') as fout:
            fout.write(message)


    @staticmethod
    def processDirectory(path, dataDir, calibrationMap, checkCoords, startLongitude, endLongitude, direction, doCleaning, angleMin, angleMax):
        if checkCoords:
            for (dirpath, dirnames, filenames) in os.walk(path):
                for name in sorted(filenames):
                    #print("infile:", name)
                    if os.path.splitext(name)[1].lower() == ".raw":
                        PreprocessRawFile.processRawFile(os.path.join(dirpath, name), dataDir, calibrationMap, startLongitude, endLongitude, direction)
                break

        if doCleaning:
            for (dirpath, dirnames, filenames) in os.walk(dataDir):
                for name in sorted(filenames):
                    #print("infile:", name)
                    if os.path.splitext(name)[1].lower() == ".raw":
                        PreprocessRawFile.cleanRawFile(os.path.join(dirpath, name), calibrationMap, angleMin, angleMax)
                break

