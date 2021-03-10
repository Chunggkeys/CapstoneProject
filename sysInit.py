from pySMC100.smc100 import * 
from ioInterface import *

## Placeholder classes 
class SampleGUI:
    def __init__(self):
        self.msg = "this is a sample gui"
        print("Initializing user interface..")
    
    def msg(self):
        return self.msg

class SampleDB:
    def __init__(self):
        self.msg = "this is a sample db"
        print("Initializing connection to database...")
    
    def msg(self):
        return self.msg

class SampleHW:
    def __init__(self):
        self.msg = "this is a sample piece of hw"
        print("Initializing hardware...")

    def msg(self):
        return self.msg
##


def mechSysInit(port):
    motor = SMC100(123, port, silent=False)
    # motor.home()
    return motor

def guiInit():
    # Display should startup here
    
    gui = SampleGUI()
    return gui

def dbInit():
    db = SampleDB()
    return db

def hwInit():
    hw = SampleHW()
    return hw