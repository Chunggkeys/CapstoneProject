from constants import *

class Control:
    def __init__(self):
        self.dataBuffer = None
        self.running = False
        self.isStopPressed = False
    
    def setDataBuffer(self, params):
        self.dataBuffer = params
    
    def setStopPressed(self, value):
        self.isStopPressed = value

    def getDataBuffer(self):
        return self.dataBuffer
    
    def isStopPressed(self):
        return self.isStopPressed
    
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