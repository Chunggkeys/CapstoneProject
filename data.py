from datetime import datetime
from mesomatdbtools.dbconnector import DBConnector
import numpy as np

class Data:
    def __init__(self):
        self.testName = "TempName"
        # Timestamp
        self.Time = []
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

    def appendData(self, **kwargs):
        for key, val in kwargs.items():
            if val == None:
                continue # dont append if no value
            if key == "Time":
                self.Time.append(val)
            elif key == "R0":
                self.R0.append(val)
            elif key == "R1":
                self.R1.append(val)
            elif key == "R2":
                self.R2.append(val)
            elif key == "R3":
                self.R3.append(val)
            elif key == "V0":
                self.V0.append(val)
            elif key == "V1":
                self.V1.append(val)
            elif key == "V2":
                self.V2.append(val)
            elif key == "V3":
                self.V3.append(val)
            elif key == "Temp":
                self.Temp.append(val)
            elif key == "SampleTime":
                self.SampleTime.append(val)
            elif key == "MotorPosition":
                self.MotorPosition.append(val)

    def _getDataTuple(self):
        output = (  ["Time"] + self.Time,
                    ["R0"] + self.R0,
                    ["R1"] + self.R1,
                    ["R2"] + self.R2,
                    ["R3"] + self.R3,
                    ["V0"] + self.V0,
                    ["V1"] + self.V1,
                    ["V2"] + self.V2,
                    ["V3"] + self.V3,
                    ["Temp"] + self.Temp,
                    ["SampleTime"] + self.SampleTime,
                    ["MotorPosition"] + self.MotorPosition
                 )
        return output

    # used for mysql upload and safety in case crash during upload
    def saveToCSV(self):
        data_tuple = self._getDataTuple()
        np.savetxt('data.csv', data_tuple, delimiter=',')


    def uploadToDatabase(self, label):
        con = DBConnector(user='alexander.dingwall@mesomat.com', \
                  password='2018', \
                  host='localhost')

        con.connect()

        date = datetime.now().strftime("%Y-%m-%d") # date looks like '2020-03-20'
        sampleIds = []

        if (',' in label):
            labels = label.split(',')
            for l in labels:
                if (con.get_by_label(l.upper() if len(l) <= 2 else l, 'samples', verbose = True) == -1):
                    con.add_sample(l.upper() if len(l) <= 2 else l,description='This sample was created automatically to match a data file added through Python.Please fill in the appropriate information.')
                sampleIds.append(con.get_by_label(l.upper() if len(l) <= 2 else l, 'samples', verbose = False))
        elif (con.get_by_label(label.upper() if len(label) <= 2 else label, 'samples', verbose = True) == -1):
            con.add_sample(label.upper() if len(label) <= 2 else label,description='This sample was created automatically to match a data file added through Python. Please fill in the appropriate information.')
            sampleIds.append(con.get_by_label(label.upper() if len(label) <= 2 else label, 'samples', verbose = False))         
        else:
            sampleIds.append(con.get_by_label(label.upper() if len(label) <= 2 else label, 'samples', verbose = False))   

        con.add_data(f[:-4],  os.path.join(dirpath,f), samples=sampleIds, data_type = test_type, date_created=date)

        con.disconnect()

