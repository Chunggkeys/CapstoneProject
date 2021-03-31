import spiConfig


import spidev
import time
import sys
import RPi.GPIO as GPIO
from array import *


#ads1220 registers
RREG  =   0x20
WREG  =   0x40
START =   0x08
STOP  =   0x0A
RDATAC=   0x10 
SDATAC=   0x11
RDATA =   0x12

GPIO.setmode(GPIO.BOARD)


# declararion
num_pins = 5
VIn = 3300
DRDY_PIN  = [5,7,11,13,15]
CS_PIN    = [29,31,33,35,37]
voltage_array  = [0, 0, 0, 0, 0]

GPIO.setwarnings(False);

#Set pin direction
for x in range(num_pins):
    GPIO.setup(CS_PIN[x],GPIO.OUT)
    GPIO.setup(DRDY_PIN[x],GPIO.IN)

spi = spidev.SpiDev()# create spi object
spi.open(0,1)# open spi port 0, device (CS)1
spi.max_speed_hz = (500000)
spi.mode = (1)


def Read_Data(x):
    volt = 0;
    buff = [0,0,0,0,0,0,0,0,0];
    #buff=array('b',[0,0,0,0,0,0,0,0,0])
    #buff = [];
    GPIO.output(CS_PIN[x], False)
    #time.sleep(0.001)               # sleep for 0.1 seconds
    #for i in range(0,9):
    buff = spi.xfer2([0xff,0xff,0xff])
    '''buff2 = spi.xfer2([0xff])
    buff3 = spi.xfer2([0xff])'''
    #buff[i] = buffer[0]
    #print("%x" %buffer[0])	
    '''channel = 1
    r = spi.xfer2([1, (8+channel)<<4, 0])
    #r = spi.xfer2([0xff],[0xff],[0xff],[0xff],[0xff],[0xff],[0xff],[0xff],[0xff])
    r = spi.xfer2([0xff])
    #adcout = ((r[0]&3) << 8)
    #print [(x) for x in buff]'''

    #time.sleep(0.002)               # sleep for 0.1 seconds
    GPIO.output(CS_PIN[x], True)

   # print("0x %x %x %x\t"%(buff[0],buff[1],buff[2]))
    value = buff[0]<<16 | buff[1]<<8 | buff[2]
 #   print(value)
    if ((float(value) >= 8388607)):
        volt = -1*((16777216-float(value)) * (3300.0)) / (8388607)
    else :
        volt = ((float(value) * (3300.0)) / 1 / (8388607))
  #  print  (x, ":", volt,"mV")

    #print("0x %x %x %x\t"%(buff[0],buff[1],buff[2]))
    '''print int(buff[0])
    print int(buff[1])'''

    '''print int(buff2[0])
    print int(buff3[0])'''


    return volt;
    #return r



def read_R(Pot):
    resistance = [0, 0, 0, 0]
    voltage_array = [0, 0, 0, 0]


    for x in range(4):
        voltage_array[x] = Read_Data(x);
        resistance[x] = (voltage_array[x] * Pot[x])/(VIn - voltage_array[x])

    return resistance

def read_T():
    resistance = 0
    voltage = Read_Data(4)

    temp_Calib = 28.82;
    temp = voltage/0.041276 + temp_Calib 
    #resistance= (voltage * Pot)/(VIn - voltage)

    return temp

while True:

    x = read_R([360,0,0,0]);
    t = read_T()
    print(x, "mV", t, "C" )
    time.sleep(0.5)

