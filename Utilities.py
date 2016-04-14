
from scipy import interpolate

class Utilities:

    @staticmethod
    def utcToSec(utc):
        t = str(int(utc))
        #print(s)
        #print(s[:2], s[2:4], s[4:])
        h = int(t[:2])
        m = int(t[2:4])
        s = int(t[4:])
        return ((h*60)+m)*60+s

    @staticmethod
    def secToTimeTag2(sec):
        #return float(time.strftime("%H%M%S", time.gmtime(sec)))
        t = sec * 1000
        s, ms = divmod(t, 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return float("%d%02d%02d%03d" % (h, m, s, ms))

    @staticmethod
    def timeTag2ToSec(tt2):
        t = str(int(tt2))
        h = int(t[:2])
        m = int(t[2:4])
        s = int(t[4:6])
        ms = int(t[6:])
        return ((h*60)+m)*60+s+(float(ms)/1000.0)

    @staticmethod
    def timestampToSec(timestamp):
        time = timestamp.split(" ")[3]
        t = time.split(":")
        h = int(t[0])
        m = int(t[1])
        s = int(t[2])
        return ((h*60)+m)*60+s

    @staticmethod
    def interp(x, y, new_x, kind='linear'):

        n0 = len(x)-1
        n1 = len(new_x)-1
        if new_x[n1] > x[n0]:
            #print(new_x[n], x[n])
            x.append(new_x[n1])
            y.append(y[n0])
        if new_x[0] < x[0]:
            #print(new_x[0], x[0])
            x.insert(0, new_x[0])
            y.insert(0, y[0])

        new_y = interpolate.interp1d(x, y, kind=kind, bounds_error=False)(new_x)

        '''
        test = False
        for i in range(len(new_y)):
            if np.isnan(new_y[i]):
                #print("NaN")
                if test:
                    new_y[i] = darkData.m_data[k][darkData.m_data.shape[0]-1]
                else:
                    new_y[i] = darkData.m_data[k][0]
            else:
                test = True
        '''

        return new_y

