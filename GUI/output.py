import numpy as np
from .constants import *


class Output():
    def __init__(self):
        self.x = []
        self.dataPos = []
        self.dataResist0 = []
        self.dataResist1 = []
        self.dataResist2 = []
        self.dataResist3 = []
        self.ptr = 0

        self.errorBuffer = []
        self.messageBuffer = []

        self.resetting = False

        self.initializeData()
    
    def initializeData(self):
        self.x = np.empty(DATA_BUFF_SIZE)
        for i in range(DATA_BUFF_SIZE):
            self.x[i] = i/20
        self.dataPos = np.empty(DATA_BUFF_SIZE)
        self.dataResist0 = np.empty(DATA_BUFF_SIZE)
        self.dataResist1 = np.empty(DATA_BUFF_SIZE)
        self.dataResist2 = np.empty(DATA_BUFF_SIZE)
        
        self.dataResist3 = np.empty(DATA_BUFF_SIZE)

    def reset(self):
        self.ptr = 0
        self.initializeData()
    
    def update(self, x, motorPos, resistance):
        # if the amount of data is less than the data buffer size
        if self.ptr < DATA_BUFF_SIZE:
            self.dataPos[self.ptr] = motorPos
            self.dataResist0[self.ptr] = resistance[0]
            self.dataResist1[self.ptr] = resistance[1]
            self.dataResist2[self.ptr] = resistance[2]
            self.dataResist3[self.ptr] = resistance[3]

            self.x[self.ptr] = x
            #print(x, motorPos, resistance)
            self.ptr +=1 

        # if the amount of data has reached the data buffer size, start removing earliest data
        else:
            self.dataPos[:-1] = self.dataPos[1:]
            self.dataPos[-1] = motorPos

            self.dataResist0[:-1] = self.dataResist0[1:]
            self.dataResist0[-1] = resistance[0]

            self.dataResist1[:-1] = self.dataResist1[1:]
            self.dataResist1[-1] = resistance[1]

            self.dataResist2[:-1] = self.dataResist2[1:]
            self.dataResist2[-1] = resistance[2]

            self.dataResist3[:-1] = self.dataResist3[1:]
            self.dataResist3[-1] = resistance[3]

            self.ptr +=  1

            self.x[:-1] = self.x[1:]
            self.x[-1] = x
    
    def getData(self):
        resistance = [self.dataResist0, self.dataResist1, self.dataResist2, self.dataResist3]
        return [self.ptr, self.x, self.dataPos, resistance]
    
    def addError(self, error):
        self.errorBuffer.append(error)
    
    def readErrors(self):
        if self.errorBuffer:
            return self.errorBuffer.pop(0)
        return None

    def addMessage(self, message):
        self.messageBuffer.append(message)
    
    def readMessages(self):
        if self.messageBuffer:
            return self.messageBuffer.pop(0)
        return None

    def isResetting(self):
        return self.resetting
    
    def setResetting(self, value):
        self.resetting = value