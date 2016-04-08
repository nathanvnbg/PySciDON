
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
                            cf = calibrationMap[key]
                            if testString.startswith(cf.m_id.upper().encode("utf-8")):
                                if i > 0:
                                    fp.read(i)

                                pos = fp.tell()
                                b = fp.read(1024)
                                fp.seek(pos)

                                #gp = contextMap[key.lower()]
                                gp = contextMap[cf.m_id]
                                if len(gp.m_attributes) == 0:
                                    gp.m_id += "_" + cf.m_id
                                    gp.m_attributes["CalFileName"] = key
                                    gp.m_attributes["FrameTag"] = cf.m_id

                                #cf = calibrationMap[key.lower()]
                                #cf = calibrationMap[key]
                                num = cf.convertRaw(b, gp)
                                fp.read(num)

                                i = 32
                                break
                        if i == 32:
                            break

        return root
