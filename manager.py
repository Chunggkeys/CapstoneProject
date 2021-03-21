from errors import *
from time import sleep

class Manager:
    
    # gui, hardware, db are all initialized instances of the gui, hardware and db
    def __init__(self, gui, hardware, db, motor):
        self.gui = gui
        self.hw = hardware
        self.db = db
        self.motor = motor
            
    # Software will pause here to wait for user input the following parameters:
    # length
    # thickness
    # deformation
    # potentiometer values
    # number of cycles
    
    def readHWStatus(self):
        pass

    def beginTest(self):
        # Assume here that parameters are correct and motor is at "home" position
        pass

    def waitUserInput(self):
        #Placeholder code
        print("Waiting for user input...")
        sleep(5)
        #

        ## Following code will be completed during integration
        # while 1:
        #     data = self.gui.checkDataBuffer()
        #     if data is not None:
        #         break
        ##


# class State:
#     def __init__(self):
#         pass

#     def 
    
class MachineState:

    def __init__(self):
        pass

class ExecutionState:
    
    def __init__(self):
        pass