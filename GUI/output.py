import numpy as np
from constants import *

class Output():
    def __init__(self):
        self.x = []
        self.dataPos = []
        self.dataResist0 = []
        self.dataResist1 = []
        self.dataResist2 = []
        self.dataResist3 = []
        self.ptr = 1

        self.error = ''
        self.messageBuffer = []

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

        self.dataPos[0] = 0
        self.dataResist0[0] = 0
        self.dataResist1[0] = 0
        self.dataResist2[0] = 0
        self.dataResist3[0] = 0

    def reset(self):
        self.ptr = 1
        self.initializeData()
    
    def update(self, x, motorPos, resistance):
        if self.ptr < DATA_BUFF_SIZE:
            self.dataPos[self.ptr] = motorPos

            self.dataResist0[self.ptr] = resistance[0]
            self.dataResist1[self.ptr] = resistance[1]
            self.dataResist2[self.ptr] = resistance[2]
            self.dataResist3[self.ptr] = resistance[3]

            self.x[self.ptr] = x

            self.ptr +=1 
        else:
            self.dataPos[:-1] = self.dataPos[1:]
            self.dataPos[-1] = motorPos[0]

            self.dataResist0[:-1] = self.dataResist[1:]
            self.dataResist0[-1] = resist[0]

            self.dataResist1[:-1] = self.dataResist1[1:]
            self.dataResist1[-1] = resist[1]

            self.dataResist2[:-1] = self.dataResist2[1:]
            self.dataResist2[-1] = resist[2]

            self.dataResist3[:-1] = self.dataResist3[1:]
            self.dataResist3[-1] = resist[3]

            self.ptr +=  1

            self.x[:-1] = self.x[1:]
            self.x[-1] = x
    
    def getData(self):
        resistance = [self.dataResist0, self.dataResist1, self.dataResist2, self.dataResist3]
        return [self.ptr, self.x, self.dataPos, resistance]
    
    def setError(self, error):
        self.error = error
    
    def getError(self):
        return self.error

    def addMessage(self, message):
        self.messageBuffer.append(message)
    
    def readMessages(self):
        if self.messageBuffer:
            return self.messageBuffer.pop(0)
        return None