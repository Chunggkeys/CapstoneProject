from manager import Manager
from sysInit import *
# import gui
# import hardware functions
# import db

PORT = "/dev/serial0"
MACHINE_STATES = {
    "IDLE" : 0,
    "EXECUTING" : {
        "HOMING" : 1,
        "CALIBRATING" : 2,
        "MOVING_DOWN" : 3,
        "MOVING_UP" : 4
    },
    "FAULTED" : 5,
    "FAILED": -1
}

# while 1:
motor = mechSysInit(PORT)
gui = guiInit()
db = dbInit()
hw = hwInit()

startState = MACHINE_STATE["IDLE"]
# manager = Manager(gui, hw, db, motor)
# manager.waitUserInput()

#Placeholder code
    print("Waiting for user input...")
    sleep(5)
    #

    ## Following code will be completed during integration
    # while 1:
    #     inputData = gui.checkDataBuffer()
    #     if inputData is not None:
    #         break
    ##

# At this point, gui will have user input already
while 
    # manager.beginTest()




