from math import sqrt
from dataclasses import dataclass, field

CALIBRATION_GAP = 10

@dataclass
class ResistanceSet:
    isCalibrated: bool = field(default=False)
    __mean: float = field(default=0.0)
    __prev_mean: float = field(default=0.0)
    __var: float = field(default=0.0)
    __std: float = field(default=0.0)
    __n: int = field(default=0)
    __count: int = field(default=0)
    __buf: list = field(default_factory=list)

    def __str__(self):
        return "isCalibrated: " + str(self.isCalibrated) +  "  __mean: " + str(self.__mean) + "  __std: " + str(self.__std)

    def add(self,val):
        self.__n += 1

        self.__buf.append(val)

        if (self.__n > CALIBRATION_GAP):

            __n = self.__n - CALIBRATION_GAP
            __val = self.__buf.pop(0)

            # update parameters
            self.__prev_mean = self.__mean
            self.__mean = self.__mean + (__val - self.__mean) / __n
            if __n > 2:
                self.__var = ( (__n - 2) * self.__var  + (__val - self.__mean ) * (__val - self.__prev_mean) ) / (__n - 1)
                self.__std = sqrt(self.__var)

            if (__n > 2 and self.__std > 1e-16 and (__val - self.__mean) / self.__std > 2):
                self.__count += 1
            else:
                self.__count = 0
            
            if (self.__count > 5):
                self.isCalibrated = True


    def clear(self):
        self.isCalibrated = False
        self.__mean = 0.0
        self.__prev_mean = 0.0
        self.__var = 0.0 
        self.__std = 0.0
        self.__n = 0
        self.__count = 0
        self.__buf.clear()

class Calibration:
    def __init__(self):

        self.allResistors = [
            ResistanceSet(),
            ResistanceSet(),
            ResistanceSet(),
            ResistanceSet()            
            ]

        self.__numData = 0
        self.isCalibrated = False
    
    def getCalibrationState(self):
        # any fibre is calibrated
        return any([r.isCalibrated for r in self.allResistors])
        
    def insertCalibrationData(self, data):
       
        self.__numData += 1

        # Adds newest data to calibration data buffer for each resistor
        # Removes the oldest data once capacity of buffer has reached CALIBRATION_MAX_LENGTH
        for d, r in zip(data, self.allResistors):
            r.add(d)
            print(r)
    
    def resetCalibrationData(self):



        for r in self.allResistors:
            r.clear()
         
        self.__numData = 0



    def getData(self):
        return self.allResistanceStats
    
    # def getNumData(self):
    #     return self.__numData