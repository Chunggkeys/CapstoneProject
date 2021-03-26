class Controller:
    def __init__(self, motor):
        self.motor = motor

        self.idleState = 0
        self.homingState = 1
        self.calibratingState = 2
        self.movingDownState = 3
        self.movingUpState = 4 
        self.faultedState = 5
        self.testCompleteState = 6
        self.failedState = -1

        self.calibrationResistances = [0,0,0,0]
        self.zeros = [0,0,0,0]

    def run(self):
        self.curState = self.homingState
        self.curCycle = 1

        while 1:
            self.status = self.motor.get_status()[1][0]
            if self.status == '0' or self.status == '10' or self.status == '11':
                self.curState = faultedState

            if self.curState == self.calibratingState:
                # calibration value currently set to 14

                # LEFT OFF HERE, CREATE SAMPLE TESTERS
                if self.calibrationResistances != self.zeros:
                    self.curState += 1
                

                self.motor.move_absolute_mm(14)
                self.curState += 1
        
            elif self.curState == self.movingDownState:
                self.motor.move_absolute_mm(self.totalDisplacement, waitStop=False)
                pos = self.motor.get_position_mm()

                if pos >= self.totalDisplacement:
                    self.motor.stop()
                    curState += 1

            elif self.curState == self.movingUpState:
                self.motor.move_absolute_mm(self.calibrationValue, waitStop=False)
                pos = self.motor.get_position_mm()

                if pos <= self.calibrationValue:   
                    self.motor.stop()
                    if self.curCycle == self.totalCycles:
                        self.curState = self.testCompleteState
                    else:
                        self.curState -= 1; self.curCycle += 1
    
            elif self.curState == self.faultedState:
                # Retry curent cycle
                self.motor.move_absolute_mm(self.calibrationValue)
            
            elif self.curState == self.failedState:
                # self.motor.home()
                # self.curState = self.homingState
                break

        return

    def setParams(self, totalCycles, displacement, calibrationDisplacement):
        self.totalCycles = totalCycles        
        self.calibrationValue = calibrationValue
        self.totalDisplacement = self.calibrationValue + displacement

    def setCalibrationResistances(self, resistanceArr):
        self.calibrationResistances = resistanceArr

    def getCurState(self):
        return self.curState
    
    def getStatus(self):
        return self.status