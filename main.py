import threading
import time
import sys

from sysInit import *
from controller import Controller
from calibration import Calibration
from manager import Manager

# Port used on the Rapberry Pi, where the driver is connected to
PORT = "/dev/ttyUSB0"

# Developer mode, flip this flag to false to run with real components
# Flip to false to use placeholder classes. 
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
totalDisplacement = 0

# measurementData = Queue()
motor = mechSysInit(PORT, False)
guiOutput, guiControl = guiInit(devMode)
db, dbKeys = dbInit(devMode)
hw = hwInit(devMode)
control = Controller(motor)

curState = IDLE_STATE
startPressed = False
dbData = {}

# Set standard out to print to params.log file
# All print statements will now print to this log
sys.stdout = open('params.log', 'w')

while 1:
    while 1:

        # Loop executes until user input is submitted
        inputData = guiControl.getDataBuffer()
        if inputData is not None:
            totalCycles = inputData['nCycles']
            displacement = inputData['defn']

            guiControl.clearDataBuffer()
            curState = CALIBRATING_STATE
            break
    
    # totalDisplacement = displacement + calibrationDisplacement
    control.setParams(totalCycles, displacement)

    # Initialize SPI communication to allow temperature and resistance
    # measurement
    hw.initialisation1()
    hw.initialisation2()

    # Start controller on another thread
    t = threading.Thread(target=control.run, args=())
    t.start()
    
    while 1:
        state = control.getCurState()
        pos = control.getPos()

        if state == MOVING_DOWN_STATE or state == MOVING_UP_STATE:
            # As actuator is moving up and down, resistance data and temperature
            # are being read and stored into hash
            data = hw.read_R()
            temp = hw.read_T()

            t = time.time()

            dbData[dbKeys.key_time] = t
            dbData[dbKeys.key_mpos] = pos
            dbData[dbKeys.key_res0] = data[0]
            dbData[dbKeys.key_res1] = data[1]
            dbData[dbKeys.key_res2] = data[2]
            dbData[dbKeys.key_res3] = data[3]
            
            db.appendData(**dbData)

            # Update live graph
            guiOutput.update(t, pos, data)

        elif state == CALIBRATING_STATE:
            # Calibration using statistical analysis, t-test
            c = Calibration()
            while not c.getCalibrationState():
                data = hw.read_R()
                c.insertCalibrationData(data)
                control.setCalibrated(c.getCalibrationState())

        elif state == FAILED_STATE:
            # Controller errors obtained and gui displays error message
            controllerErrors = control.getErrorBuffer()
            guiOutput.addMessage("Test has failed")
            break

        elif state == TEST_COMPLETE_STATE:
            # Controller completes test, gui displays message
            guiOutput.addMessage("Test Complete!")
            break

    hw.close()

    # Data uploaded to database here
    db.uploadToDatabase("sample,label,here")

    # Flags reset for the next test
    startPressed = False; inputData = None
    curState = IDLE_STATE; curCycle = 1




