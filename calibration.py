from math import sqrt

CALIBRATION_MAX_LENGTH = 50

class Calibration:
    def __init__(self):

        self.allResistanceStats = {
            "r1" : {
                "queue" : [],
                "mean" : 0,
                "var" : 0,
                "stDev" : 0,
                "firstCalib" : 0
            },
            "r2" : {
                "queue" : [],
                "mean" : 0,
                "var" : 0,
                "stDev" : 0,
                "firstCalib" : 0
            },
            "r3" : {
                "queue" : [],
                "mean" : 0,
                "var" : 0,
                "stDev" : 0,
                "firstCalib" : 0
            },
            "r4" : {
                "queue" : [],
                "mean" : 0,
                "var" : 0,
                "stDev" : 0,
                "firstCalib" : 0
            }
        }

        self.allResistors = self.allResistanceStats.keys()

        self.numData = 0
        self.isCalibrated = False
    
    def getCalibrationState(self):
        return self.isCalibrated
        
    def insertCalibrationData(self, data):
       
        self.numData += 1

        # Adds newest data to calibration data buffer for each resistor
        # Removes the oldest data once capacity of buffer has reached CALIBRATION_MAX_LENGTH
        index = 0 
        for r in self.allResistors:
            self.allResistanceStats[r]["queue"].append(data[index])

            if self.numData > CALIBRATION_MAX_LENGTH:
                self.allResistanceStats[r]["firstCalib"] = self.allResistanceStats[r]["queue"].pop(0)

            index += 1            

        # Updates t-value every time new data is added
        self._updateT(data)

    def resetCalibrationData(self):
        index = 0 
        for r in self.allResistors:
            self.allResistanceStats[r]["queue"] = []
            index += 1            
        self.numData = 0
    
    def _updateT(self, data):
        index = 0
        for r in self.allResistors:
            val = data[index]
            curMean = self.allResistanceStats[r]["mean"]
            curVar = self.allResistanceStats[r]["var"]
            
            prevMean = curMean

            # New mean calculation with new data
            if self.numData <= CALIBRATION_MAX_LENGTH:
                curMean = prevMean + (val - prevMean) / self.numData
            else:
                oldVal = self.allResistanceStats[r]["firstCalib"] / CALIBRATION_MAX_LENGTH
                curMean = prevMean - oldVal + val / CALIBRATION_MAX_LENGTH
                

            self.allResistanceStats[r]["mean"] = curMean

            # variance and standard deviation only calculated when there are more than
            # two data points
            if self.numData > 2:
                curVar = ((self.numData-2) * curVar + (val-curMean) * (val-prevMean)) / (self.numData-1)
                self.allResistanceStats[r]["var"] = curVar
                self.allResistanceStats[r]["stDev"] = sqrt(curVar)
        
            index += 1
        
            # Toggles isCalibrated flag once standard deviation is greater than, equal to 2
            if self.allResistanceStats[r]["stDev"] >= 2:
                self.isCalibrated = True; break

    def getData(self):
        return self.allResistanceStats
    
    # def getNumData(self):
    #     return self.numData