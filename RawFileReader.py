
import sys

class RawFileReader:
    MAX_TAG_READ = 32
    MAX_BLOCK_READ = 1024
    SATHDR_READ = 128

    # Function for reading SATHDR (Header) messages
    # Messages are in format: SATHDR <Value> (<Name>)\r\n
    @staticmethod
    def readSATHDR(hdr):

        if sys.version_info[0] < 3:
            end = hdr.find(b"\x0D\x0A".decode("string_escape"))
        else:
            end = hdr.find(bytes(b"\x0D\x0A".decode("unicode_escape"), "utf-8"))

        sp1 = hdr.find(b" ")
        sp2 = hdr.rfind(b" ")

        if sys.version_info[0] < 3:
            str1 = hdr[sp1+1:sp2]
            str2 = hdr[sp2+2:end-1]
        else:
            str1 = hdr[sp1+1:sp2].decode('utf-8')
            str2 = hdr[sp2+2:end-1].decode('utf-8')
        #print(str1, str2)

        if len(str1) == 0:
            str1 = "Missing"
        return (str2, str1)

    # Reads a raw file
    @staticmethod
    def readRawFile(filepath, calibrationMap, contextMap, root):

        posframe = 1

        # Note: Prosoft adds posframe=1 to the GPS for some reason
        print(contextMap.keys())
        gp = contextMap["$GPRMC"]
        ds = gp.getDataset("POSFRAME")
        ds.appendColumn(u"COUNT", posframe)
        posframe += 1

        with open(filepath, 'rb') as f:
            while 1:
                # Reads binary file to find message frame tag
                pos = f.tell()
                b = f.read(RawFileReader.MAX_TAG_READ)
                f.seek(pos)

                if not b:
                    break

                #print b
                for i in range(0, RawFileReader.MAX_TAG_READ):
                    testString = b[i:].upper()
                    #print("test: ", testString[:6])

                    if i == RawFileReader.MAX_TAG_READ-1:
                        f.read(RawFileReader.MAX_TAG_READ)
                        break

                    # Detects message type from frame tag
                    if testString.startswith(b"SATHDR"):
                        #print("SATHDR")
                        if i > 0:
                            f.read(i)
                        hdr = f.read(RawFileReader.SATHDR_READ)
                        (k,v) = RawFileReader.readSATHDR(hdr)
                        root.m_attributes[k] = v

                        break
                    else:
                        num = 0
                        for key in calibrationMap:
                            cf = calibrationMap[key]
                            if testString.startswith(cf.m_id.upper().encode("utf-8")):
                                if i > 0:
                                    f.read(i)

                                pos = f.tell()
                                msg = f.read(RawFileReader.MAX_BLOCK_READ)
                                f.seek(pos)

                                gp = contextMap[cf.m_id]
                                if len(gp.m_attributes) == 0:
                                    gp.m_id += "_" + cf.m_id
                                    gp.m_attributes["CalFileName"] = key
                                    gp.m_attributes["FrameTag"] = cf.m_id

                                num = cf.convertRaw(msg, gp)
                                
                                # Generate POSFRAME
                                ds = gp.getDataset("POSFRAME")
                                ds.appendColumn(u"COUNT", posframe)
                                posframe += 1

                                f.read(num)

                                break
                        if num > 0:
                            break

 