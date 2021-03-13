# from pySMC100.smc100 import * 
# from ioInterface import *
import time

## Placeholder classes 
class SampleGUIControl:
    def __init__(self):
        self.msg = "this is a sample gui control"
        print("Initializing gui control")
    
    def msg(self):
        return self.msg

    def waitStart(self):
        time.sleep(1)
        print("start button pressed")
        return True
    
    def getDataBuffer(self):
        time.sleep(1)
        print("Grabbed data from display")
        data = { 
            'length' : 10,
            'thick' : 2,
            'defn' : 3,
            'ptt1' : 25,
            'ptt2' : 30,
            'ptt3' : 35,
            'ptt4' : 40,
            'nCycles' : 5 
        }
        return data
        


class SampleGUIOutput:
    def __init__(self):
        self.msg = "this is a sample gui output"
        print("Initializing gui output...")

        def msg(self):
            return self.msg
        
        def sendData(self, data):
            print("sending data to output")
            return
        
        def displayError(self, errorCode, msg):
            print("Error sent to display")


class SampleDB:
    def __init__(self):
        self.msg = "this is a sample db"
        print("Initializing connection to database...")
    
    def msg(self):
        return self.msg

    def sendData(self, data):
        self.data = data
        print("data sent")
        return

class SampleHW:
    def __init__(self):
        self.msg = "this is a sample piece of hw"
        print("Initializing hardware...")

    def msg(self):
        return self.msg

class SampleMotor:
    def __init__(self):
        self.msg = "this is a sample motor"
        print("Initializing motor...")

    def msg(self):
        return self.msg

    def home(self):
        print("Homing motor")
        return 0
    
    def move_relative_mm(self, dist_mm, waitStop=True):
        time.sleep(1)
        print("Moving stage downwards to ", dist_mm)
##


def mechSysInit(port, devMode=False):
    if not devMode:
        motor = SMC100(123, port, silent=False)
        motor.home()
    else:
        motor = SampleMotor()
    # motor.home()
    return motor

def guiInit():
    # Display should startup here
    guiOutput = SampleGUIOutput()
    guiControl = SampleGUIControl()
    return guiOutput, guiControl

def dbInit():
    db = SampleDB()
    return db

def hwInit():
    hw = SampleHW()
    return hw