#WORK IN PROGRESS
#DOESNT DO ANYTHING RN

import numpy as np

class Output():
    def __init__(self):
        self.x = []
        self.dataDef = []
        self.dataResist = []
        self.ptr = 1

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
    
    def update(self, x, dataDef, dataResist):
        self.x = x
        self.dataDef = dataDef
        self.dataResist = dataResist