FULL_DISPLACEMENT = 50

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
        self.curState = self.idleState

        self.errorBuffer = []

    def run(self):
        self.curState = self.calibratingState
        self.curCycle = 1

        while 1:
            self.status = self.motor.get_status()[1][0]
            if self.status == '0' or self.status == '10' or self.status == '11':
                self.errorBuffer.append("Controller error code: " + self.status + "\n")
                self.curState = self.faultedState

            if self.curState == self.calibratingState:
                # calibration value currently set to 14
                self.motor.move_absolute_mm(14)

                # LEFT OFF HERE, CREATE SAMPLE TESTERS
                # if self.calibrationResistances != self.zeros:
                #     self.curState += 1

                # self.motor.move_absolute_mm(14)
                self.curState += 1
        
            elif self.curState == self.movingDownState:
                self.motor.move_absolute_mm(self.totalDisplacement, waitStop=False)
                pos = self.motor.get_position_mm()

                if pos >= self.totalDisplacement:
                    self.motor.stop()
                    self.curState += 1

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
                # Retry current cycle
                self.motor.stop()
                self.motor.move_absolute_mm(self.calibrationValue, waitStop=False)
                if self.status == '32' or self.status == '33':
                    self.errorBuffer.append("Controller error code: " + self.status + "\nWARNING: Motor has not been reset\n")
                    self.curState = self.failedState
            
            elif self.curState == self.failedState:
                # self.motor.home()
                # self.curState = self.homingState
                break
        
            elif self.curState == self.testCompleteState:
                break
        return

    def setParams(self, totalCycles, displacement, calibrationValue):
        self.totalCycles = totalCycles        
        # self.calibrationValue = calibrationValue
        self.calibrationValue = 14
        self.totalDisplacement = self.calibrationValue + displacement

    def setCalibrationResistances(self, resistanceArr):
        self.calibrationResistances = resistanceArr
    
    def getErrorBuffer(self):
        return self.errorBuffer

    def getCurState(self):
        return self.curState
    
    def getStatus(self):
        return self.status