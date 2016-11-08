
import os
import sys
import time

from HDFDataset import HDFDataset
from HDFGroup import HDFGroup

from config import settings


class PreprocessRawFile:
    MAX_TAG_READ = 32
    MAX_BLOCK_READ = 1024
    SATHDR_READ = 128
    RESET_TAG_READ = MAX_TAG_READ-16
    
    # GPS:
    # Start 123 56.2 W
    # End 123 21.3 W

    @staticmethod
    def dateFromInt(d):
        s = str(int(d)).zfill(6)
        return time.strftime("%Y%m%d", time.strptime(s, "%d%m%y"))

    # Creates a raw file
    # Inputs:
    # gpGPSStart - Start GPS group
    # gpGPSEnd - End GPS Group
    # header - raw file header
    # messageStart - Start index of message in raw file
    # messageEnd - End index of message in raw file
    @staticmethod
    def createRawFile(gpGPSStart, gpGPSEnd, direction, f, header, messageStart, messageEnd):
        # Determine filename from date/time
        startDate = str(int(gpGPSStart.getDataset("DATE").m_columns["NONE"][0]))
        endDate = str(int(gpGPSEnd.getDataset("DATE").m_columns["NONE"][0]))
        startTime = str(int(gpGPSStart.getDataset("UTCPOS").m_columns["NONE"][0])).zfill(6)
        endTime = str(int(gpGPSEnd.getDataset("UTCPOS").m_columns["NONE"][0])).zfill(6)

        # Reformate date
        startDate = PreprocessRawFile.dateFromInt(startDate)
        endDate = PreprocessRawFile.dateFromInt(endDate)

        # Determine direction
        lonStart = gpGPSStart.getDataset("LONPOS").m_columns["NONE"][0]
        lonEnd = gpGPSEnd.getDataset("LONPOS").m_columns["NONE"][0]
        course = 'W'
        if lonStart > lonEnd:
            course = 'E'

        if direction == course:
            # Copy block of messages between start and end
            pos = f.tell()
            f.seek(messageStart)
            message = f.read(messageEnd-messageStart)
            f.seek(pos)

            filename = startDate + "T" + startTime + "_" + endDate + "T" + endTime + ".raw"
            print("Write:" + filename)

            # Write file
            data = header + message
            with open(os.path.join("Data", filename), 'wb') as fout:
                fout.write(data)
            #message = ""

    # Reads a raw file
    @staticmethod
    def processRawFile(filepath, calibrationMap, startLongitude, endLongitude, direction):

        print("Read: " + filepath)

        gpsState = 0
        gpGPSStart = None
        gpGPSEnd = None

        header = b""
        msg = b""
        #message = b""
        
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

        with open(filepath, 'rb') as f:
            while 1:
                # Reads binary file to find message frame tag
                pos = f.tell()
                b = f.read(PreprocessRawFile.MAX_TAG_READ)
                f.seek(pos)

                if not b:
                    break

                #print b
                for i in range(0, PreprocessRawFile.MAX_TAG_READ):
                    testString = b[i:].upper()
                    #print("test: ", testString[:6])

                    # Reset file position on max read
                    if i == PreprocessRawFile.MAX_TAG_READ-1:
                        #f.read(PreprocessRawFile.MAX_TAG_READ)
                        f.read(PreprocessRawFile.RESET_TAG_READ)
                        break

                    # Detects message type from frame tag
                    if testString.startswith(b"SATHDR"):
                        #print("SATHDR")
                        if i > 0:
                            f.read(i)
                        header += f.read(PreprocessRawFile.SATHDR_READ)

                        break
                    else:
                        num = 0
                        for key in calibrationMap:
                            cf = calibrationMap[key]
                            if testString.startswith(b"$GPRMC") and testString.startswith(cf.m_id.upper().encode("utf-8")):
                                if i > 0:
                                    f.read(i)

                                pos = f.tell()
                                msg = f.read(PreprocessRawFile.MAX_BLOCK_READ)
                                f.seek(pos)

                                gp = HDFGroup()
                                num = cf.convertRaw(msg, gp)

                                if num >= 0:
                                    f.read(num)
                                    #if gpsState == 0:
                                    #    msg = f.read(num)
                                    #else:
                                    #    msg += f.read(num)


                                #gp.printd()
                                if gp.hasDataset("LONPOS"):
                                    #print("has gps")
                                    lonData = gp.getDataset("LONPOS")
                                    longitude = lonData.m_columns["NONE"][0]
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
                                    else:
                                        if gpsState == 1:
                                            #print("Test")
                                            PreprocessRawFile.createRawFile(gpGPSStart, gpGPSEnd, direction, f, header, iStart, iEnd)
                                        gpsState = 0

                                break
                        if num > 0:
                            break
            # In case file finished processing without reaching endLongitude
            if gpsState == 1:
                if gpGPSStart is not None and gpGPSEnd is not None:
                    PreprocessRawFile.createRawFile(gpGPSStart, gpGPSEnd, direction, f, header, iStart, iEnd)


    @staticmethod
    def processDirectory(path, calibrationMap, startLongitude, endLongitude, direction):
        for (dirpath, dirnames, filenames) in os.walk(path):
            for name in sorted(filenames):
                #print("infile:", name)
                if os.path.splitext(name)[1].lower() == ".raw":
                    PreprocessRawFile.processRawFile(os.path.join(dirpath, name), calibrationMap, startLongitude, endLongitude, direction)
            break
