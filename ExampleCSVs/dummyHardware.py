
# dummy hardware by serving data from previous csv files

class DummyHW:
    def __init__(self, file_name):
        # Resistances
        self.R0 = []
        self.R1 = []
        self.R2 = []
        self.R3 = []
        # Voltages
        self.V0 = []
        self.V1 = []
        self.V2 = []
        self.V3 = []
        # Various other values
        self.Temp = []
        self.SampleTime = []
        self.MotorPosition = []
        self._parse_csv(file_name)

    def _parse_csv(self, file_name):
        

    def getVoltages(self):
        return 

    def getResistances(self):
        return

    def getTemp(self):
        return

    def getMotorPos(self):
        return