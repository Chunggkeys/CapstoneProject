import time

####### Uncomment when flipping devMode to False
# from pySMC100.smc100 import * 
# from GUI.control import *
# from GUI.output import *
# import GUI.gui as gui
# from ioInterface import *
########

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
        self.data = { 
            'length' : 10,
            'thick' : 2,
            'defn' : 3,
            'ptt1' : 25,
            'ptt2' : 30,
            'ptt3' : 35,
            'ptt4' : 40,
            'nCycles' : 5 
        }
        return self.data
    
    def clearDataBuffer(self):
        self.data = None

class SampleGUI:
    def __init__(self):
        self.msg = "This is a sample gui"
        print("Initialiizng gui..")

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
            print("Error sent to display with code: ",errorCode)

        def displayTestComplete(self):
            print("Test completed")


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
        # motor.home()
    else:
        motor = SampleMotor()
    # motor.home()
    return motor

def guiInit(devMode=False):
    # Display should startup here
    if devMode:
        guiOutput = SampleGUIOutput()
        guiControl = SampleGUIControl()
        gui = SampleGUI()
    else:
        guiOutput = Output()
        guiControl = Control()
        gui.main() #?????
        
    return guiOutput, guiControl

def dbInit(devMode=False):
    db = SampleDB()
    return db

def hwInit(devMode=False):
    if devMode:
        hw = SampleHW()
    else:
        hw = IOInterface()
    return hw