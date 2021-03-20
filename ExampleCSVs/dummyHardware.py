import numpy as np
import os
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

        # fill above lists vvv
        self._parse_csv(os.path.abspath(os.path.join(__file__.strip(os.path.basename(__file__)),file_name)))

    def _parse_csv(self, file_name):
        index_dict = {"R0": -1,
                      "R1": -1,
                      "R2": -1,
                      "R3": -1,
                      "V0": -1,
                      "V1": -1,
                      "V2": -1,
                      "V3": -1,
                      "Temperature": -1,
                      "Motor Position": -1,
                      }
        with open(file_name, 'r') as f:
            lines = f.readlines()
            header = lines.pop(0).strip("\n").split(",")
            for i, elem in enumerate(header):
                if elem in index_dict:
                    index_dict[elem] = i

            arrays = list(index_dict.keys())
            indexs = list(index_dict.values())

            for line in lines:
                for i, elem in enumerate(line.strip("\n").split(",")):
                    key = ""
                    try:
                        key = arrays[indexs.index(i)]
                    except:
                        continue
                    if key == "R0":
                        self.R0.append(elem)
                    elif key == "R1":
                        self.R1.append(elem)
                    elif key == "R2":
                        self.R2.append(elem)
                    elif key == "R3":
                        self.R3.append(elem)
                    elif key == "V0":
                        self.V0.append(elem)
                    elif key == "V1":
                        self.V1.append(elem)
                    elif key == "V2":
                        self.V2.append(elem)
                    elif key == "V3":
                        self.V3.append(elem)
                    elif key == "Temperature":
                        self.Temp.append(elem)
                    elif key == "Motor Position":
                        self.MotorPosition.append(elem)
        

    def getVoltages(self, fiber_index):
        value = None
        try:
            if fiber_index == 0:
                value = self.V0.pop(0)
            elif fiber_index == 1:
                value = self.V1.pop(0) 
            elif fiber_index == 2:
                value = self.V2.pop(0) 
            elif fiber_index == 3:
                value = self.V3.pop(0) 
        except:
            pass
        return value
        return 

    def getResistance(self, fiber_index):
        value = None
        try:
            if fiber_index == 0:
                value = self.R0.pop(0)
            elif fiber_index == 1:
                value = self.R1.pop(0) 
            elif fiber_index == 2:
                value = self.R2.pop(0) 
            elif fiber_index == 3:
                value = self.R3.pop(0) 
        except:
            pass
        return value

    def getTemp(self):
        value = None
        try:
            value = self.Temp.pop(0)
        except:
            pass
        return value

    def getMotorPos(self):
        value = None
        try:
            value = self.MotorPosition.pop(0)
        except:
            pass
        return value

    def __str__(self):
        out = ""
        for i in range(len(self.MotorPosition)):
            out += str(self.R0[i]) + "\t"
            out += str(self.R1[i]) + "\t"
            out += str(self.R2[i]) + "\t"
            out += str(self.R3[i]) + "\t"
            out += str(self.V0[i]) + "\t"
            out += str(self.V1[i]) + "\t"
            out += str(self.V2[i]) + "\t"
            out += str(self.V3[i]) + "\t"
            out += str(self.Temp[i]) + "\t"
            out += str(self.MotorPosition[i])
            out += "\n"
        return out