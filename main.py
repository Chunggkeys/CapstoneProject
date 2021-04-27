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
pot = []
totalDisplacement = 0

motor = mechSysInit(PORT, False)
guiOutput, guiControl = guiInit(False)
db, dbKeys = dbInit(devMode)
hw = hwInit(False)
control = Controller(motor)

curState = IDLE_STATE
startPressed = False
dbData = {}

# Set standard out to print to params.log file
# All print statements will now print to this log
# sys.stdout = open('params.log', 'w')

try: 

    while 1:
        print("Awaiting test start")

        # Start controller on another thread
        t = threading.Thread(target=control.run, args=())
        t.start()

        while 1:

            # Loop executes until user input is submitted
            guiOutput.setResetting(False)
            inputData = guiControl.getDataBuffer()
            if inputData is not None:
                totalCycles = inputData['n']
                displacement = inputData['d']
                label = inputData['label']
                pot = [inputData['p1'], inputData['p2'], inputData['p3'], inputData['p4']]
                print(pot)
                time.sleep(5)

                guiControl.clearDataBuffer()
                curState = CALIBRATING_STATE
                break
        
        # totalDisplacement = displacement + calibrationDisplacement

        control.setParams(totalCycles, displacement)

        # pot = [680,680,680,680]


        # Initialize SPI communication to allow temperature and resistance
        # measurement
        hw.initialisation1()
        hw.initialisation2()

        startTime = time.time()

        while 1:
            state = control.getCurState()
            pos = control.getPos()
            
            # Checks if user has pressed the stop button
            if guiControl.isStopPressed:
                control.kill()
                guiOutput.setResetting(True)

            if state == MOVING_DOWN_STATE or state == MOVING_UP_STATE:
                # As actuator is moving up and down, resistance data and temperature
                # are being read and stored into hash
                data = hw.read_R(pot)
                temp = hw.read_T()

                t = time.time() - startTime

                dbData[dbKeys.key_time] = t
                dbData[dbKeys.key_mpos] = pos
                dbData[dbKeys.key_res0] = data[0]
                dbData[dbKeys.key_res1] = data[1]
                dbData[dbKeys.key_res2] = data[2]
                dbData[dbKeys.key_res3] = data[3]
                
                db.appendData(**dbData)

                # Update live graph
                guiOutput.update(t, pos, data)

            elif state == HOMING_STATE:
                #print("HOMING STATE")
                pass

            elif state == CALIBRATING_STATE:
                # Calibration using statistical analysis, t-test
                isCalibrated = False
                c = Calibration()
                while not c.getCalibrationState():

                    data = hw.read_R(pot)
                    pos = control.getPos()                    
  
                    t = time.time() - startTime
                    guiOutput.update(t, pos, data)

                    #print("CALIBRATING WITH: ", data)
                    c.insertCalibrationData(data)
                    control.setCalibrated(c.getCalibrationState())

                control.setCalibrated(c.getCalibrationState())
            
            elif state == FAULTED_STATE:
                # Tells GUI that system is resetting
                guiOutput.setResetting(True)
                guiControl.setStopPressed(False)

            elif state == FAILED_STATE:
                # Controller errors obtained and gui displays error message
                controllerErrors = control.getErrorBuffer()
                guiOutput.addError("Test has failed")
                break

            elif state == TEST_COMPLETE_STATE:
                # Controller completes test, gui displays message
                guiOutput.addMessage("Test Complete!")
                control.reset()
                break

        hw.close()

        # Data uploaded to database here
        db.uploadToDatabase(label)

        # Flags reset for the next test
        startPressed = False; inputData = None
        curState = IDLE_STATE; curCycle = 1

except:
    control.kill()
    raise


