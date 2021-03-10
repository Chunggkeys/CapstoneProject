from gpiozero import LED, Pin
from time import sleep
from errors import *
from sysInit import *
import random

led1 = LED(2)
errLED = LED(3)
errors = []

# Toggled based on sensor value
isEnclosed = False

guiInputData = {
    "length" : 0,
    "thickness" : 0,
    "displacement" : 0,
    "potentiometer": 0
}

errLED.off()

# set condition for inits?
sysOK = True

def getError():

    errVal = random.randint(0,1)
    if errVal == 0:
        return False
    else: 
        return True

def sampleFunc1():
    global sysOK
    # Do task
    if random.randint(0, 5) == 0:
        errors.append(ActuatorError("ActuatorError has been raised"))
        sysOK = False
    else:
        print("Doing actuator task...")

def sampleFunc2():
    global sysOK

    # Do task
    if random.randint(0, 5) == 0:
        errors.append(CircuitError("CircuitError has been raised"))
        sysOK = False
    else:
        print("Doing circuit task...")

# Calibration?
# Initialize mechanical system
#   Assign a pin for ready state

# Initialize database comms system
#   Assign a pin for ready state

# Initialize gui system
#   Assign a pin for ready state

# simulated wait for GUI input
#   - Length
#   - Thickness
#   - Actuator displacement
#   - Potentiometer Control
timeUntilStart = random.randint(1,5)
sleep(timeUntilStart)

while 1:
    sampleFunc1()
    sampleFunc2()
    if not sysOK:
        errLED.on()
        break
    print(sysOK)
    print(errors)
    
    sleep(2)

# Send errors to GUI
for i in errors:
    print(i.message)

