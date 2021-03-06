import time

####### Uncomment when flipping devMode to False, comment when flipping to True
# from pySMC100.smc100 import * 
# from multiprocessing import Process
import threading
from GUI.control import *
from GUI.output import *
from GUI.gui import initGUI
# from ioInterface import *
# from data import Data, Common
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
            'l' : 10,
            't' : 2,
            'd' : 3,
            'p1' : 25,
            'p2' : 30,
            'p3' : 35,
            'p4' : 40,
            'n' : 5 
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
    
    def uploadToDatabase(self, label):
        print("Uploading to database")
        return
    
    def appendData(self, **kwargs):
        print("adding data to buffer")
        return

class SampleDBKeys:
    key_time = "Time"
    key_res0 = "R0"
    key_res1 = "R1"
    key_res2 = "R2"
    key_res3 = "R3"
    key_vol0 = "V0"
    key_vol1 = "V1"
    key_vol2 = "V2"
    key_vol3 = "V3"
    key_temp = "Temperature"
    key_stime = "Sample Time"
    key_mpos = "Motor Position"

class SampleHW:
    def __init__(self):
        self.msg = "this is a sample piece of hw"
        print("Initializing hardware...")

    def msg(self):
        return self.msg
    
    def read_R(self,devMode=False):
        if devMode:
            return [20,2,20,20]
        else:
            #TODO
            return 0

    def read_T(self,devMode=False):
        if devMode:
            return 20
        else:
            #TODO
            return 0

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
        print("Moving stage to ", dist_mm)
    
    def get_position_mm(self):
        return 4
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
        t = threading.Thread(target=initGUI, args=(guiControl,guiOutput,))
        t.start()
        # p = Process(target=initGUI, args=(guiControl,guiOutput,))
        # p.start()
        # p.join()
        # initGUI(guiControl, guiOutput)
        
    return guiOutput, guiControl

def dbInit(devMode=False):
    if devMode:
        db = SampleDB()
        return db, SampleDBKeys
    else:
        db = Data()
        return db, Common

def hwInit(devMode=False):
    if devMode:
        hw = SampleHW()
    else:
        hw = IOInterface()
    return hw