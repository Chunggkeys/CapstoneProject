from statistics import fmean, stdev
from math import sqrt

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

        self.numData = 0
        self.isCalibrated = False
        self.cstd = 0
        self.cmean = 0
        self.cvar = 0 
    
    # def isCalibrated(self):
    #     for i in self.allResistances:
    #         muArr = i[0:OBS_LENGTH]
    #         xArr = i[MU_START_INDEX:]
    #         t = self._tTest(xArr, muArr)

    #         # Sample t value is 2, will test later
    #         if t > 2:
    #             return True

    def insertDataPoint(self, data):
        if self.numData >= MAX_LENGTH:
            self.queueR1.pop(0)
            self.queueR2.pop(0)
            self.queueR3.pop(0)
            self.queueR4.pop(0)
        else:
            self.numData += 1

        self.queueR1.append(data[0])
        self.queueR2.append(data[1])
        self.queueR3.append(data[2])
        self.queueR4.append(data[3])

    
    def _tTest(self, xArr, muArr):
        sampleSize = len(xArr)
        xMean = fmean(xArr)
        muMean = fMean(muArr)
        stdDev = stdev(xArr)
        t = (xMean - muMean)/(stdDev / sqrt(sampleSize))
        return t