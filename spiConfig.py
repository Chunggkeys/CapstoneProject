
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

print ("test")

count = 0

def Reg_Write(address,data):    # write Fibonacci series up to 
    for x in range(num_pins):
        print ("Writing %s to Register %s" %( hex(data),hex(address)))
        print(data);


        opcode1 = (address<<2) | 0x40

        GPIO.output(CS_PIN[x], False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(CS_PIN[x], True)
        time.sleep(0.002)               # sleep for 0.1 seconds

        GPIO.output(CS_PIN[x], False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        resp = spi.xfer2([opcode1])        # transfer one byte
        resp = spi.xfer2([data])        # transfer one byte
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(CS_PIN[x], True)
    return;

def Reg_read(address):    # write Fibonacci series up to
    for x in range(num_pins):
        print ("Reading from Register %s" %(hex(address)))
        opcode1 = address | 0x20

        GPIO.output(CS_PIN[x], False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(CS_PIN[x], True)
        time.sleep(0.002)               # sleep for 0.1 seconds

        GPIO.output(CS_PIN[x], False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        resp = spi.xfer2([opcode1])        # transfer one byte
        resp = spi.xfer2([0xff])        # transfer one byt
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(CS_PIN[x], True)

        #print("Data read is %s" %(hex(resp)))
        print(resp);
    return;

def Spi_command(command):    # write Fibonacci series up to
    for x in range(num_pins):
        GPIO.output(CS_PIN[x], False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(CS_PIN[x], True)
        time.sleep(0.002)               # sleep for 0.1 seconds

        GPIO.output(CS_PIN[x], False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        resp = spi.xfer2([command])        # transfer one byte
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(CS_PIN[x], True)

    return;


def initialisation1():  
    print ("INITIALISATION");



    Spi_command(START);
    time.sleep(0.1);
    Spi_command(STOP);
    time.sleep(0.1);
    Spi_command(SDATAC);
    time.sleep(0.3);

    Reg_Write(0x00, 0x01);
    time.sleep(0.01); 
    Reg_Write(0x01, 0x04);
    time.sleep(0.01); 
    Reg_Write(0x02, 0b11010000);
    time.sleep(0.01);
    Reg_Write(0x03, 0x00);
    time.sleep(0.01);

    Reg_read(0x00);
    time.sleep(0.1);
    Reg_read(0x04);
    time.sleep(0.1);
    Reg_read(0x08);
    time.sleep(0.1);
    Reg_read(0x0c);



        
    Spi_command(RDATAC);
    time.sleep(0.3); 

    Spi_command(START);
    time.sleep(0.1);
     
    for x in range(num_pins):
        GPIO.output(CS_PIN[x], True)
    return;

def toHex(dec):
    x = (dec % 16)
    digits = "0123456789ABCDEF"
    rest = dec / 16
    if (rest == 0):
        return digits[x]
    return toHex(rest) + digits[x]

def initialisation2():

    time.sleep(0.2)
    print ("STARTED")

    #GPIO.output(CS_PIN, False)
    resp = spi.xfer2([0x11])        # transfer one byte
    time.sleep(0.3)	
    return;


initialisation1()
initialisation2()