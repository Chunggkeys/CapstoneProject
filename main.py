from manager import Manager
from sysInit import *
# from multiprocessing import Process, Queue


import time
import functions

from controller import Controller

# import gui
# import hardware functions
# import db

PORT = "/dev/ttyUSB0"
devMode = True

IDLE_STATE                  = 0
HOMING_STATE                = 1
CALIBRATING_STATE           = 2
MOVING_DOWN_STATE           = 3
MOVING_UP_STATE             = 4 
FAULTED_STATE               = 5
TEST_COMPLETE_STATE         = 6
FAILED_STATE                = -1

curCycle = 1
totalCycles = 0; displacement = 0
calibrationDisplacement = 14
totalDisplacement = 0

# measurementData = Queue()
motor = mechSysInit(PORT, devMode)
guiOutput, guiControl = guiInit(devMode)
db, dbKeys = dbInit(devMode)
hw = hwInit(devMode)
control = Controller(motor)

curState = IDLE_STATE
startPressed = False
dbData = {}

while 1:
    while 1:
        inputData = guiControl.getDataBuffer()
        if inputData is not None:
            totalCycles = inputData['nCycles']
            displacement = inputData['length']
            guiControl.clearDataBuffer()
            curState = CALIBRATING_STATE
            break
    
    totalDisplacement = displacement + calibrationDisplacement
    # control = Controller(motor, totalCycles, displacement, calibrationDisplacement)
    control.setParams(totalCycles, displacement, calibrationDisplacement)

    t = threading.Thread(target=control.run, args=(,))
    t.start()
    while 1:
        state = control.getCurState()
        if state == MOVING_DOWN_STATE or state == MOVING_UP_STATE:
            data = hw.read_R(devMode)
            temp = hw.read_T(devMode)

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
            guioutput.update(t, pos, data)
        elif state == CALIBRATING_STATE:
            data = hw.read_R(devMode)
            control.setCalibrationResistances(data)
        elif state == FAILED_STATE:
            guiOutput.addMessage("Test has failed")
            break

            
    # At this point, gui will have user input already
    # This loop controls motor 
    # while curState >= HOMING_STATE and curState <= MOVING_UP_STATE:
    #     if curState == HOMING_STATE:
    #         motor.home()
    #         print(curState)
    #         curState += 1
    #     elif curState == CALIBRATING_STATE:
    #         # motor.home()
    #         # Calibration to be implemented, hardcoded at 14 mm temporarily
    #         motor.move_absolute_mm(calibrationDisplacement)

    #         print(curState)
    #         curState += 1
    #     elif curState == MOVING_DOWN_STATE:
    #         # Motor displaces downward
    #         motor.move_absolute_mm(totalDisplacement)


    #         data = hw.read_R(devMode)
    #         temp = hw.read_T(devMode)

    #         # Change to something better
    #         t = time.time()
    #         pos  = motor.get_position_mm()
    #         guiOutput.update(t, pos, data)

    #         dbData[dbKeys.key_time] = t
    #         dbData[dbKeys.key_mpos] = pos
    #         dbData[dbKeys.key_res0] = data[0]
    #         dbData[dbKeys.key_res1] = data[1]
    #         dbData[dbKeys.key_res2] = data[2]
    #         dbData[dbKeys.key_res3] = data[3]
            
    #         db.appendData(**dbData)

    #         # Need to include error handling
    #         if pos >= totalDisplacement:
    #             curState += 1

    #     elif curState == MOVING_UP_STATE:
    #         # Motor displaces upward
    #         motor.move_absolute_mm(calibrationDisplacement, waitStop=False)
    #         if pos <= calibrationDisplacement:
    #             if curCycle == totalCycles:
    #                 curState = HOMING_STATE
    #             elif curCycle < totalCycles:
    #                 curState -= 1

    #         print(curState)
    #     elif curState == FAULTED_STATE:
    #         # Retry most recent action?
    #         print(curState)
    #     elif curState == TEST_COMPLETE_STATE: 
    #         guiOutput.addMessage("Test Complete!")
    #         motor.home()
    #         break
    #     elif curState == FAILED_STATE:
    #         print(curState)    
    #         guiOutput.setError(msg)
    #         curState = IDLE_STATE

    db.uploadToDatabase("sample,label,here")
    startPressed = False; inputData = None
    curState = IDLE_STATE; curCycle = 1




