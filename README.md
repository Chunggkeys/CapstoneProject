# CommunicationSystem

## Main script (main.py)

This script is the main call script that acts as the centerpiece of the entire system.
System initialization is performed here, along with gathering measurements, system calibration, and database operations. This script is implemented as a main loop that doesn't allow further execution until data has been inputted via the GUI. The test then begins and performs different actions based on the motor state (i.e perform calibration calculations, read temperature/resistance values etc...). At the end of the test, data is sent to database.

Note that the motor controller runs on a separate thread.

Neat features:
- At roughly line 16, this is a developer mode flag that will determine whether or not sample classes will be used. This is useful if, for example, you would like to add features to only the GUI. Then you can flip the devMode variable to true, but pass in "False" to guiInit at line 33. This change will only have the GUI work, but all other software components will use sample classes in sysInit.py (explained later)
- At roughly line 44, you'll see a line of code that dictates the location of standard output (i.e python "print" statements). By default, these statements would show on the console. However, by uncommenting that line of code, all "print" statements will be redirected to a file that you specify. This is intended to be a logging mechanism that will allow more thorough debugging or perhaps system monitoring. 

## System Initialization (sysInit.py)

This script is used to initialize all software components:
- Motor controller
- Database
- GUI
- IO interface

First thing you will notice in this script is a number of sample classes. These are the sample classes mentioned earlier. They are by no means robust, so feel free to modify them as necessary. These classes act as substitutes for the actual classes and contain methods that will simply for continuous execution of the main script. Ideally, these sample classes would contain all the methods that the actual classes have. 

Further down, you'll see the code that is necessary to initialize the individual software components. You see the relevance of devMode from the main script and what it does.

Note here that the GUI is run on its own thread. This is **absolutely necessary** due to the limitations of the framework of choice (PyQT5).

## Motor controller (controller.py)

This script is used to control the motion of the motor. The design of this controller is similar to the first version of this device. At each iteration of an infinite while loop, the position of the motor is determined, and the state of the motor changes depending on that position, along with the previous state. The notable difference between this version and the previous version is the change necessary to accommodate for multithreading. The "run" method is executed continuously on a separate thread from the main thread.

## Measurement Module

The Measurement Module contains the code for reading the ADC values and returning the resistances, and temperature values to the manager module. The configurations of the ADC's can be changed in the initialisation1 function and can be referenced by section 8.6.1 of the [ADS1220 data sheet](https://www.ti.com/lit/ds/symlink/ads1220.pdf?ts=1620014551609&ref_url=https%253A%252F%252Fwww.ti.com%252Fproduct%252FADS1220). read_R uses the Read_Data function to read ADC's 1-4 corresponding to the ADC's used for the sample fibres, and read_T reads ADC5 used for reading the thermocouples. 
