#import spiConfig


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

# GPIO.setmode(GPIO.BOARD)


# declaration
NUM_PINS = 5
V_IN = 3300
DRDY_PIN  = [5,7,11,13,15]
CS_PIN    = [29,31,33,35,37]

# Is this necessary?
voltage_array  = [0, 0, 0, 0, 0]


#Set pin direction
# for x in range(NUM_PINS):
#     GPIO.setup(CS_PIN[x],GPIO.OUT)
#     GPIO.setup(DRDY_PIN[x],GPIO.IN)

# spi = spidev.SpiDev()# create spi object
# spi.open(0,1)# open spi port 0, device (CS)1
# spi.max_speed_hz = (500000)
# spi.mode = (1)

class HW:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0,1)
        self.spi.max_speed_hz = (500000)
        self.spi.mode = (1)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        for x in range(NUM_PINS):
            GPIO.setup(CS_PIN[x],GPIO.OUT)
            GPIO.setup(DRDY_PIN[x],GPIO.IN)

        self.init1Completed = False
        self.init2Completed = False

    def Reg_Write(self,address,data):    # write Fibonacci series up to 
        for x in range(NUM_PINS):
            #print ("Writing %s to Register %s" %( hex(data),hex(address)))
            #print(data);


            opcode1 = (address<<2) | 0x40

            GPIO.output(CS_PIN[x], False)
            time.sleep(0.002)               # sleep for 0.1 seconds
            GPIO.output(CS_PIN[x], True)
            time.sleep(0.002)               # sleep for 0.1 seconds

            GPIO.output(CS_PIN[x], False)
            time.sleep(0.002)               # sleep for 0.1 seconds
            resp = self.spi.xfer2([opcode1])        # transfer one byte
            resp = self.spi.xfer2([data])        # transfer one byte
            time.sleep(0.002)               # sleep for 0.1 seconds
            GPIO.output(CS_PIN[x], True)
        return;

    def Reg_Write_Pin(self, cs_pin, address, data):

        opcode1 = (address<<2) | 0x40

        GPIO.output(cs_pin, False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(cs_pin, True)
        time.sleep(0.002)               # sleep for 0.1 seconds

        GPIO.output(cs_pin, False)
        time.sleep(0.002)               # sleep for 0.1 seconds
        resp = self.spi.xfer2([opcode1])        # transfer one byte
        resp = self.spi.xfer2([data])        # transfer one byte
        time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(cs_pin, True)

    def Reg_read(self,address):    # write Fibonacci series up to
        for x in range(NUM_PINS):
            #print ("Reading from Register %s" %(hex(address)))
            opcode1 = address | 0x20

            GPIO.output(CS_PIN[x], False)
            time.sleep(0.002)               # sleep for 0.1 seconds
            GPIO.output(CS_PIN[x], True)
            time.sleep(0.002)               # sleep for 0.1 seconds

            GPIO.output(CS_PIN[x], False)
            time.sleep(0.002)               # sleep for 0.1 seconds
            resp = self.spi.xfer2([opcode1])        # transfer one byte
            resp = self.spi.xfer2([0xff])        # transfer one byt
            time.sleep(0.002)               # sleep for 0.1 seconds
            GPIO.output(CS_PIN[x], True)

            ##print("Data read is %s" %(hex(resp)))
            #print(resp);
        return;

    def Spi_command(self, command):    # write Fibonacci series up to
        for x in range(NUM_PINS):
            GPIO.output(CS_PIN[x], False)
            time.sleep(0.002)               # sleep for 0.1 seconds
            GPIO.output(CS_PIN[x], True)
            time.sleep(0.002)               # sleep for 0.1 seconds

            GPIO.output(CS_PIN[x], False)
            time.sleep(0.002)               # sleep for 0.1 seconds
            resp = self.spi.xfer2([command])        # transfer one byte
            time.sleep(0.002)               # sleep for 0.1 seconds
            GPIO.output(CS_PIN[x], True)

        return;


    def initialisation1(self):  

        if not self.init1Completed:
            #print ("INITIALISATION");

            self.Spi_command(START);
            time.sleep(0.1);
            self.Spi_command(STOP);
            time.sleep(0.1);
            self.Spi_command(SDATAC);
            time.sleep(0.3);

            self.Reg_Write(0x00, 0x01);
            time.sleep(0.01); 
            self.Reg_Write(0x01, 0x04);
            time.sleep(0.01); 
            self.Reg_Write(0x02, 0b11010000);
            time.sleep(0.01);
            self.Reg_Write(0x03, 0x00);
            time.sleep(0.01);

            self.Reg_read(0x00);
            time.sleep(0.1);
            self.Reg_read(0x04);
            time.sleep(0.1);
            self.Reg_read(0x08);
            time.sleep(0.1);
            self.Reg_read(0x0c);

            self.Spi_command(RDATAC);
            time.sleep(0.3); 

            self.Spi_command(START);
            time.sleep(0.1);
            
            for x in range(NUM_PINS):
                GPIO.output(CS_PIN[x], True)
        
            self.init1Completed = True
        else:
            pass

        return;

    def toHex(dec):
        x = (dec % 16)
        digits = "0123456789ABCDEF"
        rest = dec / 16
        if (rest == 0):
            return digits[x]
        return toHex(rest) + digits[x]

    def initialisation2(self):

        if not self.init2Completed:
            time.sleep(0.2)
            ##print ("STARTED")

            #GPIO.output(CS_PIN, False)
            resp = self.spi.xfer2([0x11])        # transfer one byte
            time.sleep(0.3)	

            self.init2Completed = True
        
        else:
            pass

        return;


    def Read_Data(self,x):
        volt = 0;
        buff = [0,0,0,0,0,0,0,0,0];
        #buff=array('b',[0,0,0,0,0,0,0,0,0])
        #buff = [];
        while GPIO.input(DRDY_PIN[x]) == True:
            time.sleep(0.001)

        GPIO.output(CS_PIN[x], False)
        #time.sleep(0.001)               # sleep for 0.1 seconds
        #for i in range(0,9):

        buff = self.spi.xfer2([0xff,0xff,0xff])
        '''buff2 = spi.xfer2([0xff])
        buff3 = spi.xfer2([0xff])'''
        #buff[i] = buffer[0]
        ##print("%x" %buffer[0])	
        '''channel = 1
        r = spi.xfer2([1, (8+channel)<<4, 0])
        #r = spi.xfer2([0xff],[0xff],[0xff],[0xff],[0xff],[0xff],[0xff],[0xff],[0xff])
        r = spi.xfer2([0xff])
        #adcout = ((r[0]&3) << 8)
        ##print [(x) for x in buff]'''

        #time.sleep(0.002)               # sleep for 0.1 seconds
        GPIO.output(CS_PIN[x], True)

    # #print("0x %x %x %x\t"%(buff[0],buff[1],buff[2]))
        value = buff[0]<<16 | buff[1]<<8 | buff[2]
    #   #print(value)
        if ((float(value) >= 8388607)):
            volt = -1*((16777216-float(value)) * (3300.0)) / (8388607)
        else :
            volt = ((float(value) * (3300.0)) / 1 / (8388607))
    #  #print  (x, ":", volt,"mV")

        ##print("0x %x %x %x\t"%(buff[0],buff[1],buff[2]))
        '''#print int(buff[0])
        #print int(buff[1])'''

        '''#print int(buff2[0])
        #print int(buff3[0])'''


        return volt;
        #return r

    def select_mux_channels(self, cs_pin, channel):

        if channel == 1:
            code = 0x00
        else:
            code = 0x50

        reg0 = 0x01
        reg0 = reg0 & ~0xF0
        reg0 = reg0 | code

        self.Reg_Write_Pin(cs_pin, 0x00, reg0)

    def read_R(self, Pot):
        resistance = [0, 0, 0, 0]
        voltage_array = [0, 0, 0, 0]
        pot = [680,680,680,680]

        for x in range(4):
            voltage_array[x] = self.Read_Data(x);
            resistance[x] = (voltage_array[x] * Pot[x])/(V_IN - voltage_array[x])

        return resistance

    def read_T(self):
        resistance = 0
        self.select_mux_channels(CS_PIN[4], 1)
        v1 = self.Read_Data(4)
        self.select_mux_channels(CS_PIN[4], 2)
        v2 = self.Read_Data(4)

        temp_Calib = 28.82;
        t1 = v1/0.041276 + temp_Calib 
        t2 = v2/0.041276 + temp_Calib 



        #resistance= (voltage * Pot)/(V_IN - voltage)

        return (t1,t2)

    def close(self):
        self.spi.close()



# Test code
# hw = HW()
# hw.initialisation1()
# hw.initialisation2()

# while True:

#     x = hw.read_R([680,680,680,680]);
#     t = hw.read_T()
#     #print(x, "mV", t, "C" )

