from constants import *

class Control:
    #temp values
    # MAX_LENGTH = 100
    # MAX_THICK = 20
    # MAX_DEF = 50
    # MAX_CYCLES = 65535
    # MAX_POT = 2000

    def __init__(self):
        self.dataBuffer = None
        self.running = False
    
    def setDataBuffer(self, params):
        self.dataBuffer = params
    
    def setRunning(self, value):
        self.running = value

    def getDataBuffer(self):
        return self.dataBuffer
    
    def getRunning(self):
        return self.running
    
    def clearDataBuffer(self):
        self.dataBuffer = None
    
    def validateParams(self, params):
        invalid = []
        if params['l'] < 0 or params['l'] > MAX_LENGTH:
            invalid.append('l')
        if params['t'] < 0 or params['t'] > MAX_THICK:
            invalid.append('t')
        if params['d'] < 0 or params['d'] > MAX_DEF:
            invalid.append('d')
        if params['n'] < 0 or params['n'] > MAX_CYCLES:
            invalid.append('n')
        if params['p1'] < 0 or params['p1'] > MAX_POT:
            invalid.append('p1')
        if params['p2'] < 0 or params['p2'] > MAX_POT:
            invalid.append('p2')
        if params['p3'] < 0 or params['p3'] > MAX_POT:
            invalid.append('p3')
        if params['p4'] < 0 or params['p4'] > MAX_POT:
            invalid.append('p4')
        
        return invalid