from datetime import datetime
from .mesomatdbtools.dbconnector import DBConnector
from dataclasses import dataclass
import numpy as np

@dataclass
class Common:
        key_time = "Time"
        key_res0 = "R0"
        key_res1 = "R1"
        key_res2 = "R2"
        key_res3 = "R3"
        key_vol0 = "V0"
        key_vol1 = "V1"
        key_vol2 = "V2"
        key_vol3 = "V3"
        key_temp = "Temperature"
        key_stime = "Sample Time"
        key_mpos = "Motor Position"
        
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

        # User Info For DataBase
        self.user = 'alexander.dingwall@mesomat.com'
        self.pw   = '2018'
        self.host = 'localhost'

    def appendData(self, **kwargs):
        for key, val in kwargs.items():
            if val == None:
                continue # dont append if no value
            if key == Common.key_time:
                self.Time.append(val)
            elif key == Common.key_res0:
                self.R0.append(val)
            elif key == Common.key_res1:
                self.R1.append(val)
            elif key == Common.key_res2:
                self.R2.append(val)
            elif key == Common.key_res3:
                self.R3.append(val)
            elif key == Common.key_vol0:
                self.V0.append(val)
            elif key == Common.key_vol1:
                self.V1.append(val)
            elif key == Common.key_vol2:
                self.V2.append(val)
            elif key == Common.key_vol3:
                self.V3.append(val)
            elif key == Common.key_temp:
                self.Temp.append(val)
            elif key == Common.key_stime:
                self.SampleTime.append(val)
            elif key == Common.key_mpos:
                self.MotorPosition.append(val)

    def _getDataTuple(self):
        output = (  [Common.key_time] + self.Time,
                    [Common.key_res0] + self.R0,
                    [Common.key_res1] + self.R1,
                    [Common.key_res2] + self.R2,
                    [Common.key_res3] + self.R3,
                    [Common.key_vol0] + self.V0,
                    [Common.key_vol1] + self.V1,
                    [Common.key_vol2] + self.V2,
                    [Common.key_vol3] + self.V3,
                    [Common.key_temp] + self.Temp,
                    [Common.key_stime] + self.SampleTime,
                    [Common.key_mpos] + self.MotorPosition
                 )
        return output

    # used for mysql upload and safety in case crash during upload
    def saveToCSV(self):
        data_tuple = self._getDataTuple()
        
        with open("test_data.csv", 'w') as fw:
            
            for j in range(len(self.R0)):
                temp_line = ""
                for i in range(len(data_tuple)):
                    try:
                        temp_line += str(data_tuple[i][j]) + ","
                    except:
                        temp_line += "-1" + ","
                
                fw.write(temp_line[:-1]+"\n")

    # work in progress function - *Needs more testing*
    def uploadToDatabase(self, label):
        self.saveToCSV()
        con = DBConnector(user=self.user, password=self.pw, host=self.host)

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

        con.add_data("test_data",  "test_data.csv", samples=sampleIds, data_type = 'static', date_created=date)
        print("Added data")
        con.disconnect()

