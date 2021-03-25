class Controller:
    def __init__(self, motor, totalCycles, displacement, calibrationValue):
        self.motor = motor
        self.totalCycles = totalCycles
        self.calibrationValue = calibrationValue
            
        self.totalDisplacement = self.calibrationValue + displacement

        self.idleState = 0
        self.homingState = 1
        self.calibratingState = 2
        self.movingDownState = 3
        self.movingUpState = 4 
        self.faultedState = 5
        self.testCompleteState = 6
        self.failedState = -1

    def run(self):
        self.curState = self.homingState
        self.curCycle = 1

        while 1:
            self.status = self.motor.get_status()[1][0]
            if self.curState == self.calibratingState:
                # calibration value currently set to 14
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
                    # Is the stop necessary?
                    self.motor.stop()
                    if self.curCycle == self.totalCycles:
                        self.curState = self.testCompleteState
                    else:
                        self.curState -= 1; self.curCycle += 1
    
            elif self.curState == self.faultedState:
                # Retry curent cycle
                self.motor.move_absolute_mm(self.calibrationValue)
            
            elif self.curState == self.failedState:
                self.motor.home()
                self.curState = self.homingState
                break

        return
        
    def getCurState(self):
        return self.curState
    
    def getStatus(self):
        return self.status