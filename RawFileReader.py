
import sys

class RawFileReader:

    @staticmethod
    def readSATHDR(b):
        
        if sys.version_info[0] < 3:
            end = b.find(b"\x0D\x0A".decode("string_escape"))
        else:
            end = b.find(bytes(b"\x0D\x0A".decode("unicode_escape"), "utf-8"))

        sp1 = b.find(b" ")
        sp2 = b.rfind(b" ")

        if sys.version_info[0] < 3:
            str1 = b[sp1+1:sp2]
            str2 = b[sp2+2:end-1]
        else:
            str1 = b[sp1+1:sp2].decode('utf-8')
            str2 = b[sp2+2:end-1].decode('utf-8')
        #print(str1, str2)
        if len(str1) == 0:
            str1 = "Missing"
        return (str2, str1)

    # ToDo: create more dynamic detection        
    @staticmethod
    def generateContext(root):
        for gp in root.m_groups:
            frameTag = gp.m_attributes["FrameTag"]
            #print(line)
            if frameTag == "SATHED0150":
                #gp.m_id = "Reference"
                #gp.m_sensorType = "ES"
                gp.m_attributes["InstrumentType"] = "Reference"
                gp.m_attributes["Media"] = "Air"
                gp.m_attributes["MeasMode"] = "Surface"
                gp.m_attributes["FrameType"] = "ShutterDark"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.getTableHeader("ES")
                gp.m_attributes["DISTANCE_1"] = "Pressure ES 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface ES 1 1 0"
            elif frameTag == "SATHLD0151":
                #gp.m_id = "SAS"
                #gp.m_sensorType = "LI"
                gp.m_attributes["InstrumentType"] = "SAS"
                gp.m_attributes["Media"] = "Air"
                gp.m_attributes["MeasMode"] = "VesselBorne"
                gp.m_attributes["FrameType"] = "ShutterDark"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.getTableHeader("LI")
                gp.m_attributes["DISTANCE_1"] = "Pressure LI 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface LI 1 1 0"
            elif frameTag == "SATHLD0152":
                #gp.m_id = "SAS"
                #gp.m_sensorType = "LT"
                gp.m_attributes["InstrumentType"] = "SAS"
                gp.m_attributes["Media"] = "Air"
                gp.m_attributes["MeasMode"] = "VesselBorne"
                gp.m_attributes["FrameType"] = "ShutterDark"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.getTableHeader("LT")
                gp.m_attributes["DISTANCE_1"] = "Pressure LT 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface LT 1 1 0"
            elif frameTag == "SATHSE0150":
                #gp.m_id = "Reference"
                #gp.m_sensorType = "ES"
                gp.m_attributes["InstrumentType"] = "Reference"
                gp.m_attributes["Media"] = "Air"
                gp.m_attributes["MeasMode"] = "Surface"
                gp.m_attributes["FrameType"] = "ShutterLight"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.getTableHeader("ES")
                gp.m_attributes["DISTANCE_1"] = "Pressure ES 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface ES 1 1 0"
            elif frameTag == "SATHSL0151":
                #gp.m_id = "SAS"
                #gp.m_sensorType = "LI"
                gp.m_attributes["InstrumentType"] = "SAS"
                gp.m_attributes["Media"] = "Air"
                gp.m_attributes["MeasMode"] = "VesselBorne"
                gp.m_attributes["FrameType"] = "ShutterLight"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.getTableHeader("LI")
                gp.m_attributes["DISTANCE_1"] = "Pressure LI 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface LI 1 1 0"
            elif frameTag == "SATHSL0152":
                #gp.m_id = "SAS"
                #gp.m_sensorType = "LT"
                gp.m_attributes["InstrumentType"] = "SAS"
                gp.m_attributes["Media"] = "Air"
                gp.m_attributes["MeasMode"] = "VesselBorne"
                gp.m_attributes["FrameType"] = "ShutterLight"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.getTableHeader("LT")
                gp.m_attributes["DISTANCE_1"] = "Pressure LT 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface LT 1 1 0"
            elif frameTag == "SATSAS0052":
                #gp.m_id = "SAS"
                #gp.m_sensorType = "None"
                gp.m_attributes["InstrumentType"] = "SAS"
                gp.m_attributes["Media"] = "Air"
                gp.m_attributes["MeasMode"] = "VesselBorne"
                gp.m_attributes["FrameType"] = "LightAncCombined"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.m_attributes["Head_1"] = "ANC 1 1 None"
                gp.m_attributes["DISTANCE_1"] = "Pressure ANC 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface ANC 1 1 0"
                gp.m_attributes["SN"] = "0052"
            elif frameTag == "$GPRMC":
                #gp.m_id = "GPS"
                #gp.m_sensorType = "None"
                gp.m_attributes["InstrumentType"] = "GPS"
                gp.m_attributes["Media"] = "Not Required"
                gp.m_attributes["MeasMode"] = "Not Required"
                gp.m_attributes["FrameType"] = "Not Required"
                gp.m_attributes["INSTRUMENT_NO"] = "1"
                gp.m_attributes["Head_1"] = "GPS 1 1 None"
                gp.m_attributes["DISTANCE_1"] = "Pressure GPS 1 1 0"
                gp.m_attributes["DISTANCE_2"] = "Surface GPS 1 1 0"
                gp.m_attributes["VLF_INSTRUMENT"] = "$GPRMC"

    @staticmethod
    def readRawFile(filepath, calibrationMap, contextMap, root):

        with open(filepath, 'rb') as fp:
            while 1:
                pos = fp.tell()
                b = fp.read(32)
                fp.seek(pos)

                if not b:
                    break

                #print b
                for i in range(0, 32):
                    testString = b[i:].upper()
                    #print("test: ", testString[:6])

                    if i == 31:
                        fp.read(32)
                        break

                    if testString.startswith(b"SATHDR"):
                        #print("SATHDR")
                        if i > 0:
                            fp.read(i)
                        b = fp.read(128)
                        (k,v) = RawFileReader.readSATHDR(b)
                        root.m_attributes[k] = v

                        break
                    else:
                        for key in calibrationMap:
                            if testString.startswith(key.upper().encode("utf-8")):
                                if i > 0:
                                    fp.read(i)

                                pos = fp.tell()
                                b = fp.read(1024)
                                fp.seek(pos)

                                #gp = contextMap[key.lower()]
                                gp = contextMap[key]
                                if len(gp.m_attributes) == 0:
                                    gp.m_id += "_" + key
                                    gp.m_attributes["CalFileName"] = calibrationMap[key].m_name
                                    gp.m_attributes["FrameTag"] = key

                                #cf = calibrationMap[key.lower()]
                                cf = calibrationMap[key]
                                num = cf.convertRaw(b, gp)
                                fp.read(num)

                                i = 32
                                break
                        if i == 32:
                            break

        return root
