# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 13:42:49 2020

@author: User
"""

from dbconnector import DBConnector
import os

            
            
def parse_date(date):
    date = date.split("-")    
    return "{:04d}-{:02d}-{:02d}".format(int(date[0]),int(date[1]),int(date[2]))


con = DBConnector(user='alexander.dingwall@mesomat.com', \
                  password='2018', \
                  host='localhost')

con.connect()


for (dirpath, dirnames, filenames) in os.walk('..\\ToAdd'):
    for f in filenames:
        
        if (os.path.getsize(os.path.join(dirpath,f)) > 10000 and '.csv' in f):
    
            print('---')
            
            fields = f.split('_')

            if (len(fields) == 2):
                label = fields[0]
                test_type = 'static'
                date = parse_date(fields[1])
            elif (len(fields) == 3):
                label = fields[0]
                test_type = fields[1].lower()
                date = parse_date(fields[2])
                
            print("label:", label)
            
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


