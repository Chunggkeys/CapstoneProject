from manager import Manager
from sysInit import *
# import gui
# import hardware functions
# import db

doTest = True

# while 1:
motor = mechSysInit()
gui = guiInit()
db = dbInit()
hw = hwInit()

manager = Manager(gui, hw, db, motor)
manager.waitUserInput()

while doTest:

# At this point, gui will have user input already

manager.beginTest()