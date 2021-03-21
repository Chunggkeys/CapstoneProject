from manager import Manager
from sysInit import *
# from multiprocessing import Process, Queue
import time
# import functions

# import gui
# import hardware functions
# import db

PORT = "/dev/serial0"
devMode = True

IDLE_STATE = 0
HOMING_STATE = 1
CALIBRATING_STATE = 2
MOVING_DOWN_STATE = 3
MOVING_UP_STATE = 4 
FAULTED_STATE = 5
TEST_COMPLETE_STATE = 6
FAILED_STATE = -1
curCycle = 1
totalCycles = 0; displacement = 0
calibrationDisplacement = 0

# measurementData = Queue()
motor = mechSysInit(PORT, devMode)
guiOutput, guiControl = guiInit()
db, dbKeys = dbInit(devMode)
hw = hwInit(devMode)

curState = IDLE_STATE
startPressed = False
dbData = {}

while 1:
    while 1:
        inputData = guiControl.getDataBuffer()
        print(inputData)
        if inputData is not None:
            totalCycles = inputData['nCycles']
            displacement = inputData['length']
            guiControl.clearDataBuffer()
            break
    #

    # Tentatively here, might be removed
    # while not startPressed:
    #     startPressed = guiControl.waitStart()
    #     curState = HOMING_STATE
    # 

    # At this point, gui will have user input already
    # This loop controls motor 
    while curState >= HOMING_STATE and curState <= MOVING_UP_STATE:
        if curState == HOMING_STATE:
            motor.home()
            print(curState)
            curState += 1
        elif curState == CALIBRATING_STATE:
            # Calibrate motor here

            print(curState)
            curState += 1
        elif curState == MOVING_DOWN_STATE:
            # Motor displaces downward
            data = hw.read_R(devMode)
            temp = hw.read_T(devMode)

            # Change to something better
            t = time.time()
            pos  = motor.get_position_mm()
            guiOutput.update(t, pos, data)

            dbData[dbKeys.key_time] = t
            dbData[dbKeys.key_mpos] = pos
            dbData[dbKeys.key_res0] = data[0]
            dbData[dbKeys.key_res1] = data[1]
            dbData[dbKeys.key_res2] = data[2]
            dbData[dbKeys.key_res3] = data[3]
            
            db.appendData(**dbData)

            # Need to include error handling
            if curCycle <= totalCycles:
                motor.move_relative_mm(displacement)
                curState += 1; curCycle += 1
            else:
                curState = TEST_COMPLETE_STATE

        elif curState == MOVING_UP_STATE:
            # Motor displaces upward
            motor.move_relative_mm(-displacement)
            print(curState)
            curState -= 1
        elif curState == FAULTED_STATE:
            # Retry most recent action?
            print(curState)
        elif curState == TEST_COMPLETE_STATE: 
            guiOutput.addMessage("Test Complete!")
            motor.home()
            break
        elif curState == FAILED_STATE:
            print(curState)    
            guiOutput.setError(msg)
            curState = IDLE_STATE

    db.uploadToDatabase("sample,label,here")
    startPressed = False; inputData = None
    curState = IDLE_STATE; curCycle = 1




