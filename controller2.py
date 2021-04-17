# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:28:04 2019

@author: alexander
"""

import serial
import time
import numpy as np
from math import sqrt


from smc100 import SMC100
from functions import getRealStrainFunction
from datetime import datetime as dt
from Data import Data

# states for state machine
RESET               = 0     # returns motor to start position
HOMING              = 1     # moves downwards until capacitive touch is detected
MEASURING_DOWN      = 2     # collect data while moving downwards
MEASURING_UP        = 3     # collect data while moving upwards
EXIT                = 4     
FAULTED             = 5

NUM_SAMPLES = 1

class Controller:
    
    
    def __init__(self, meas_com, motor_com, columns = None, show_period=False):
        
        assert(columns != None)
        
        self.meas_com = meas_com
        self.motor_com = motor_com
        
        # Connect to peripherals
        self.meas_arduino = serial.Serial(self.meas_com, 9600, timeout=0.1)
        print("Connected to Arduino on", self.meas_com)
        self.motor = SMC100(1, self.motor_com)    
        
        time.sleep(1)
        
        
        self.start_pos = 0  # set in the HOMING state
        self.end_pos = 0
        self.initial_time = 0
        self.state = RESET
        self.cycle = 0
        self.position = 0
        self.show_period = show_period
        
        
        self.calib_data = []
        self.ci=0
        self.cj=0
        self.cmean = 0
        self.cmean_prev=0
        self.cvar = 0
        self.cstd = 0
        self.fit_data = []
        self.ccount = 0
        
        self.columns = columns
        
        self.cycles = 0
        
        self.data = None
        
    def __str__(self):
        return "State: " + str(self.get_state()) + "\tCycle: " + str(self.cycle) + "/" + str(self.cycles) + " (" + str(int(100*self.cycle/float(self.cycles))) + "%)\tPosition: " + str(self.position) +  "\tMeasurement: " +  str(self.measurement[0]) +  "\tMotor Status: " +  str(self.motor.get_status()) + "\tMean: " + str(self.cmean) + "\tStd Dev: " + str(self.cstd)

    def get_state(self):
        if self.state == RESET: 
            return "RESET"
        elif self.state == HOMING:
            return "HOMING"
        elif self.state == MEASURING_DOWN:
            return "MEASURING_DOWN"
        elif self.state == MEASURING_UP:
            return "MEASURING_UP"
        elif self.state == EXIT:
            return "EXIT"
        elif self.state == FAULTED:
            return "FAULTED"
        
    def add_calibration(self, value):

        l = len(self.calib_data)
        
        if (l < self.CAL_BUF_LENGTH):
            self.calib_data.append(value)
            l+=1
            self.cj+=1
            
            self.cmean_prev = self.cmean
            self.cmean = self.cmean + (value-self.cmean) / l
            
            if(l>2): 
                self.cvar= ((l-2) * self.cvar + (value-self.cmean) * (value-self.cmean_prev)) / (l-1)
                self.cstd = sqrt(self.cvar)
            
        else:
            self.calib_data[self.ci] = value
            self.ci = (self.ci+1) % self.CAL_BUF_LENGTH
            self.cj = (self.cj+1) % self.CAL_BUF_LENGTH
            
        
        

    def configure(self, vel, min_pos, max_pos, D, L, T, K=0, R0=0, peak_current=0.21, rms_current=0.15, homing_velocity=0.5, sample="", cal_buf_length=50):
        assert(peak_current <= .3)
        assert(rms_current <= .19)
        
        
        self.velocity = vel
        self.homing_velocity = homing_velocity

        print("Configuring parameters...")
        self.motor.sendcmd("PW","1")
        time.sleep(1)
        
        self.motor.sendcmd("VA",  self.velocity)
        self.motor.sendcmd("OH",  self.homing_velocity)
        self.motor.sendcmd("QIL", peak_current)
        self.motor.sendcmd("QIR", rms_current)
             
        self.motor.sendcmd("PW","0")
        time.sleep(5)
            
        print("Velocity set to:\t\t", self.motor.sendcmd('VA','?', expect_response=True, retry=20), " mm/s")
        print("Homing/Reset velocity set to:\t", self.motor.sendcmd('OH','?', expect_response=True, retry=20), " mm/s")
        print("RMS current limit set to:\t", self.motor.sendcmd("QIR", "?", expect_response=True, retry=20), " A")
        print("Peak current limit set to:\t" + self.motor.sendcmd("QIL", "?", expect_response=True, retry=20) + " A")
    
        self.min_pos = min_pos*1000     # in um
        self.max_pos = max_pos*1000     # in um
        self.D = D*1000                 # in um
        self.L = L                      # in m
        self.T = T                      # in m
        
        self.CAL_BUF_LENGTH = cal_buf_length
        
        self.to_strain = getRealStrainFunction([-0.001,0.001],self.L,self.T/2)
        
        print("set data")
        
                
        date_time = dt.now()        
        self.data = Data(columns = self.columns, \
                 filename = '.\\Data\\'+sample.replace(' ','_') +"_"+str(date_time.year)+'-'+str(date_time.month)+'-'+str(date_time.day)+'-'+str(date_time.second)+str(date_time.microsecond)+'.csv', \
                 motor=True)
        
    def loop(self, verbose=True):
            
        self.position = self.motor.get_position_um()
        self.measurement = self.get_reading(self.meas_arduino)
                
        if verbose: print(self)
                    
        if self.state == RESET:
            
            self.add_calibration(self.measurement[0])
            
            if (self.motor.get_status()[1][0] == '0' or self.motor.get_status()[1] == '10' or self.motor.get_status()[1] == '11'):
                self.state = FAULTED
            elif (self.motor.get_status()[1] == '14'):
                self.motor.home(waitStop=False)
            else:
                self.motor.move_absolute_um(self.min_pos, waitStop=False)
                
                if self.position >= self.min_pos - 1 and self.position <= self.min_pos + 1:
                    self.motor.move_absolute_um(self.min_pos+1, waitStop=False)
                    self.motor.move_absolute_um(self.min_pos-1, waitStop=False)
                    
                if self.position == self.min_pos:
                    self.motor.stop()
                    self.state = HOMING
            
        elif self.state == HOMING:
            
            
            self.motor.move_absolute_um(self.max_pos, waitStop=False)
            self.motor.sendcmd("VA",self.homing_velocity)
        
            self.add_calibration(self.measurement[0])
            
            if (self.measurement[0] > self.cmean + self.cstd*2):
                self.ccount += 1
            
            if (self.motor.get_status()[1][0] == '0' or self.motor.get_status()[1] == '10' or self.motor.get_status()[1] == '11'):
                self.state = FAULTED
                
            elif (self.ccount > 5):
                
                self.motor.stop()
                            
                self.start_pos = self.position
                self.end_pos = self.start_pos + self.D
                
                self.state = MEASURING_DOWN
                
        elif self.state == MEASURING_DOWN:
    
            self.motor.move_absolute_um(self.end_pos, waitStop=False)
            self.motor.move_absolute_um(self.end_pos, waitStop=False)
            
            self.data.add(self.measurement, motor_pos = self.position, calc_strain = self.to_strain((self.position-self.start_pos)/1e6))
        
            
            
            if (self.motor.get_status()[1][0] == '0' or self.motor.get_status()[1] == '10' or self.motor.get_status()[1] == '11'):
                self.state = FAULTED
                
            elif self.position >= self.end_pos - 1 :
                self.motor.stop()
                self.cycle = self.cycle + 0.5
                self.state = MEASURING_UP
            
            if self.cycle >= self.cycles-.1:
                self.state = EXIT
                
        elif self.state == MEASURING_UP:
            
            
            self.motor.move_absolute_um(self.start_pos, waitStop=False)
            self.motor.move_absolute_um(self.start_pos, waitStop=False)
    
    
            self.data.add(self.measurement, motor_pos = self.position, calc_strain = self.to_strain((self.position-self.start_pos)/1e6))
            
        
            if (self.motor.get_status()[1][0] == '0' or self.motor.get_status()[1] == '10' or self.motor.get_status()[1] == '11'):
                self.state = FAULTED

            elif self.position <= self.start_pos+1:
                self.motor.stop()
                self.cycle = self.cycle + 0.5
                self.state = MEASURING_DOWN
                
            elif self.cycle >= self.cycles-.1:
                self.state = EXIT
                
        elif self.state == FAULTED:
            
            self.motor.home(waitStop=False)
            
            if (self.motor.get_status()[1] == "32" or self.motor.get_status()[1] == "33"):
                self.state = RESET
            
        elif self.state == EXIT:
            # do nothing # 
            pass
                
    def get_reading(self, arduino):
        
        data = np.array([])
        num_points=0
        
        for i in range(NUM_SAMPLES):
  
            arduino.flush()
            
            arduino.write("poke\n".encode())
            
            while True:
                
                if arduino.in_waiting:      # number of bytes in receive  buffer
                    
                    inp = str(arduino.readline())[2:-3].split(',')
                    num_points = len(inp)
                    data = np.append(data, [np.array(inp).astype(np.float)])

                    break;

        data = data.reshape((NUM_SAMPLES,num_points))
        
        return [np.average(data[:,i]) for i in range(num_points)]

  
    def run(self, cycles=None, hours=0, minutes=0, seconds=0, verbose=True):
        
    
        self.cycle = 0
        
        # start dataframe recording
        self.initial_time = time.time()
        
        
        if cycles != None:
            self.cycles = cycles
        else:
            self.cycles = round( (hours*3600 + minutes*60 + seconds) * self.velocity / (self.D * 2 / 1000) * 2) / 2.0
            
            
            
        # print time estimate      
        print("Number of cycles: " + str(self.cycles))
        estimated_time = self.cycles * self.D * 2 / self.velocity / 1000
        print( "Estimated time: " + ((str(int(estimated_time / 3600)) + " hours ") if int(estimated_time / 3600) > 0 else "") + \
               ((str(int(estimated_time%3600/60))) + " minutes " if int(estimated_time%3600/60) > 0 else "") + \
               str(int(estimated_time%60)) + " seconds"
               )
        
        
        print("Starting now...")
        
        self.state = RESET           
        
        while self.state != EXIT:
            self.loop(verbose)
            
        self.data.save()
             
    
    def close(self):
        
        try:
            self.motor.stop()
            self.motor.move_absolute_um(self.start_pos,waitStop=False)
             
            self.motor.close()
        except Exception:
            print("Failed to close motor")
        
        
        try:
            self.data.save()
        except Exception:
            print("Failed to save data");       

            
        try:
            self.meas_arduino.close()
        except Exception:
            print("Failed to close microcontroller")
        
    
        
        
    
