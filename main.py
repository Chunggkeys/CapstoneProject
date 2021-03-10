from manager import Manager
from sysInit import *
# import gui
# import hardware functions
# import db

# while 1:
motor = mechSysInit()
gui = guiInit()
db = dbInit()
hw = hwInit()

# At this point, gui will have user input already
manager = Manager(gui, hw, db, motor)
manager.waitUserInput()
manager.beginTest()