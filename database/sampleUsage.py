from data import Data, Common
from ExampleCSVs.dummyHardware import DummyHW
import time

db = Data()
dummy = DummyHW('HT_H3_aclamped_2cycles-05-06-2020-.csv')

def getAllResistances(d):
    d[Common.key_res0] = dummy.getResistance(0)
    d[Common.key_res1] = dummy.getResistance(1)
    d[Common.key_res2] = dummy.getResistance(2)
    d[Common.key_res3] = dummy.getResistance(3)
    return d

def getAllVoltages(d):
    d[Common.key_vol0] = dummy.getVoltage(0)
    d[Common.key_vol1] = dummy.getVoltage(1)
    d[Common.key_vol2] = dummy.getVoltage(2)
    d[Common.key_vol3] = dummy.getVoltage(3)
    return d



running = True
count = 0
while running:
    # time.sleep(2)
    loop_results = {}

    loop_results[Common.key_time] = time.time()
    
    loop_results = getAllResistances(loop_results)
    loop_results = getAllVoltages(loop_results)

    loop_results[Common.key_temp] = dummy.getTemp()
    loop_results[Common.key_mpos] = dummy.getMotorPos()
    if loop_results[Common.key_mpos] == None or count > 100:
        running = False

    db.appendData(**loop_results)
    count += 1
    
db.saveToCSV()