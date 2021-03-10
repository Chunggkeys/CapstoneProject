from manager import Manager
from sysInit import *
# import gui
# import hardware functions
# import db

PORT = "/dev/serial0"

IDLE_STATE = 0
HOMING_STATE = 1
CALIBRATING_STATE = 2
MOVING_DOWN_STATE = 3
MOVING_UP_STATE = 4 
FAULTED_STATE = 5
FAILED_STATE = -1

# while 1:
motor = mechSysInit(PORT, devMode=True)
gui = guiInit()
db = dbInit()
hw = hwInit()

curState = IDLE_STATE
startPressed = False

while 1:
    while 1:
        inputData = gui.checkDataBuffer()
        if inputData is not None:
            break
    #

    while not startPressed:
        startPressed = gui.waitStart()
        curState = HOMING_STATE

    # At this point, gui will have user input already
    # This loop controls motor 
    while curState >= HOMING_STATE and curState <= MOVING_UP_STATE:
        if curState == HOMING_STATE:
            motor.home()
            curState += 1
        elif curState == CALIBRATING_STATE:
            # Calibrate motor here
            curState += 1
        elif curState == MOVING_DOWN_STATE:
            # Motor displaces downward
            curState += 1
        elif curState == MOVING_UP_STATE:
            # Motor displaces upward
            curState -= 1
        elif curState == FAULTED_STATE:
            # Retry most recent action?
            pass
        elif curState == FAILED_STATE:
            
            gui.displayError(code, msg)
            curState = IDLE_STATE

    




