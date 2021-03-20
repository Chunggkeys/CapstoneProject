import numpy as np

class Output():
    DATA_BUFF_SIZE = 200

    def __init__(self):
        self.x = []
        self.dataDef = []
        self.dataResist = []
        self.ptr = 1

        self.error = ''
        self.messageBuffer = []

        self.initializeData()
    
    def initializeData(self):
        self.x = np.empty(200)
        for i in range(200):
            self.x[i] = i/20
        self.dataDef = np.empty(200)
        self.dataResist = np.empty(200)

        self.dataDef[0] = 0
        self.dataResist[0] = 0

    def reset(self):
        self.ptr = 1
        self.initializeData()
    
    def update(self, x, deformation, resist):
        if self.ptr < 200:
            self.dataDef[self.ptr] = deformation
            self.dataResist[self.ptr] = resist
            self.x[self.ptr] = x

            self.ptr +=1 
        else:
            self.dataDef[:-1] = self.dataDef[1:]
            self.dataDef[-1] = deformation

            self.dataResist[:-1] = self.dataResist[1:]
            self.dataResist[-1] = resist

            self.ptr +=  1

            self.x[:-1] = self.x[1:]
            self.x[-1] = x
    
    def getData(self):
        return [self.ptr, self.x, self.dataDef, self.dataResist]
    
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
        
OutputModule = Output()