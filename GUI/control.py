class Control:
    #temp values
    MAX_LENGTH = 100
    MAX_THICK = 20
    MAX_DEF = 50
    MAX_CYCLES = 65535
    MAX_POT = 2000

    def __init__(self):
        self.dataBuffer = None
        self.running = False
    
    def setDataBuffer(self, l, t, d, n, p1, p2, p3, p4):
        self.dataBuffer = {
            'length': l,
            'thick': t,
            'defn': d,
            'nCycles': n,
            'ptt1': p1,
            'ptt2': p2,
            'ptt3': p3,
            'ptt4': p4
        }
    
    def setRunning(self, value):
        self.running = value

    def getDataBuffer(self):
        return self.dataBuffer
    
    def getRunning(self):
        return self.running
    
    def clearDataBuffer(self):
        self.dataBuffer = None
    
    def validateParams(self, l, t, d, n, p1, p2, p3, p4):
        invalid = []
        if l < 0 or l > self.MAX_LENGTH:
            invalid.append('l')
        if t < 0 or t > self.MAX_THICK:
            invalid.append('t')
        if d < 0 or d > self.MAX_DEF:
            invalid.append('d')
        if n < 0 or n > self.MAX_CYCLES:
            invalid.append('n')
        if p1 < 0 or p1 > self.MAX_POT:
            invalid.append('p1')
        if p2 < 0 or p2 > self.MAX_POT:
            invalid.append('p2')
        if p3 < 0 or p3 > self.MAX_POT:
            invalid.append('p3')
        if p4 < 0 or p4 > self.MAX_POT:
            invalid.append('p4')
        
        return invalid


ControlModule = Control()