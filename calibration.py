from statistics import fmean, stdev

MAX_LENGTH = 55
OBS_LENGTH = 50
MU_START_INDEX = 49

class Calibration:
    def __init__(self):
        self.queueR1 = []
        self.queueR2 = []
        self.queueR3 = []
        self.queueR4 = []        

        self.allResistances = [
            self.queueR1, 
            self.queueR2, 
            self.queueR3, 
            self.queueR4
        ]
    
    def isCalibrated(self):
        for i in self.allResistances:
            muArr = i[0:OBS_LENGTH]
            xArr = i[MU_START_INDEX:]
            t = self.tTest(xArr, muArr)

            # Sample t value is 2, will test later
            if t > 2:
                return True

    def insertDataPoint(self, data):
        if len(self.queueR1) >= MAX_LENGTH:
            self.queueR1.pop(0)
        
        self.queueR1.append(data[0])
        self.queueR2.append(data[1])
        self.queueR3.append(data[2])
        self.queueR4.append(data[3])
    
    def tTest(self, xArr, muArr):
        sampleSize = len(x)
        xMean = fmean(xArr)
        muMean = fMean(muArr)
        stdDev = stdev(xArr)
        t = (xMean - muMean)/(stdDev / sqrt(sampleSize))
        return t