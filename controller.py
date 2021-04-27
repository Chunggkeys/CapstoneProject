from time import time, sleep

FULL_DISPLACEMENT = 25

milliseconds = lambda : int(time()*1000)

POS_THRESHOLD = 0.001

class Controller:
    def __init__(self, motor):
        self.motor = motor
        self.reset()

    def reset(self):

        self.idleState = 0
        self.homingState = 1
        self.calibratingState = 2
        self.movingDownState = 3
        self.movingUpState = 4 
        self.faultedState = 5
        self.testCompleteState = 6
        self.failedState = -1

        self.isCalibrated = False

        self.calibrationResistances = [0,0,0,0]
        self.zeros = [0,0,0,0]
        self.curState = self.idleState

        self.status=0
        self.state=0
    
        self.curTime = 0

        self.errorBuffer = []
        self.pos = self.motor.get_position_mm()

        self.minPos = 6

    def stateAsString(self) -> str:
        if self.curState == self.idleState: return "IDLE" 
        elif self.curState == self.homingState: return "HOMING"
        elif self.curState == self.calibratingState: return "CALIBRATING"
        elif self.curState == self.movingDownState: return "MOVING_DOWN"
        elif self.curState == self.movingUpState: return "MOVING_UP"
        elif self.curState == self.faultedState: return "FAULTED"
        elif self.curState == self.testCompleteState: return "COMPLETE"
        elif self.curState == self.failedState: return "FAILED"
        
    def __str__(self):
        return "State: " + self.stateAsString() + "  Pos: " + str(self.pos) + "  Status: " + str(self.status) 

    def getPos(self):
        return self.pos

    def run(self):
        self.curState = self.homingState
        self.curCycle = 1

        while 1:

            self.curTime = milliseconds()  
        
            print(self)

            self.status = self.motor.get_status()[1]            
            self.pos = self.motor.get_position_mm()
            
            # print("Position: " + str(self.pos))
            # print("Status: " + str(self.status))
            # print("Cycle: " + str(self.curCycle))

            if self.status == '0' or self.status == '10' or self.status == '11':
                self.errorBuffer.append("Controller error code: " + self.status + "\n")
                self.curState = self.faultedState
                

            if self.curState == self.calibratingState:
                # print("CALIBRATING STATE")
                self.motor.move_absolute_mm(FULL_DISPLACEMENT, waitStop=False)
                
                if self.isCalibrated:
                    # Actuator stops as soon as calibration is calibrated. 
                    # Motion parameters are saved and logged
                    self.motor.stop()
                    self.calibrationValue = self.motor.get_position_mm()
                    self.totalDisplacement = self.calibrationValue + self.displacement

                    # Log parameterized values
                    # print("Calibrated displacement: " + self.calibrationValue + "\nTotal displacement: " + self.totalDisplacement + "\n\n")
                    self.curState += 1
            
            if self.curState == self.homingState:
                # print("HOMING STATE")
                self.motor.move_absolute_mm(self.minPos, waitStop=False)

                if self.pos <= self.minPos + POS_THRESHOLD:
                    self.curState = self.calibratingState
        
            elif self.curState == self.movingDownState:
                # print("MOVING DOWN")
                self.motor.move_absolute_mm(self.totalDisplacement, waitStop=False)

                if self.pos >= self.totalDisplacement-POS_THRESHOLD:
                    self.motor.stop()
                    self.curState += 1

            elif self.curState == self.movingUpState:
                # print("MOVING UP")
                self.motor.move_absolute_mm(self.calibrationValue, waitStop=False)

                if self.pos <= self.calibrationValue + POS_THRESHOLD:   
                    self.motor.stop()
                    if self.curCycle == self.totalCycles:
                        self.curState = self.testCompleteState
                    else:
                        self.curState -= 1; self.curCycle += 1
    
            elif self.curState == self.faultedState:
                #  Retry current cycle
                
                self.motor.home(waitStop=False)
                
                if self.status == '32' or self.status == '33':
                    self.errorBuffer.append("Controller error code: " + self.status + "\nWARNING: Motor has not been reset\n")
                    self.curState = self.calibratingState
            
            elif self.curState == self.failedState:
                break
        
            elif self.curState == self.testCompleteState:
                break


            # t = ( 300 - (milliseconds() - self.curTime )) / 1000
            # print("Sleep: " + str(milliseconds()-self.curTime))
            # sleep(0 if t < 0 else t)

        return

    def setParams(self, totalCycles, displacement):
        self.totalCycles = totalCycles        
        # self.totalDisplacement = self.calibrationValue + displacement
        self.displacement = displacement
    
    def getErrorBuffer(self):
        return self.errorBuffer

    def getCurState(self):
        return self.curState
    
    def getStatus(self):
        return self.status

    def setCalibrated(self, isCalibrated):
        self.isCalibrated = isCalibrated

    def kill(self):
        self.motor.stop()
        self.motor.move_absolute_mm(self.minPos)