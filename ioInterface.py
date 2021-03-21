from gpiozero import Pin

class IOInterface:
    def __init__(self):
        self.vOut1 = Pin(3)
        self.vOut2 = Pin(4)
        self.vOut3 = Pin(17)
        self.vOut4 = Pin(27)
        self.thermistor = Pin(22)
    
    def getThermistorOutput(self):
        return self.thermistor
    
    def getVoltageOutput(self):
        return self.vOut1, self.vOut2, self.vOut3, self.vOut4