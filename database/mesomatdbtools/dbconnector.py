# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 11:40:48 2020


file: dbconnector.py

The main class for interacting with the database. This will let you add/edit/delete
new samples, fibres, plots, and data; add new tables/columns; and query the
tables and return results in an easy to parse format.


@author: Alexander
"""


from .exceptions import AuthenticationError, TableNotFoundError, ColumnNotFoundError, InvalidParameterError, InvalidIdError

import mysql.connector as mysql
from mysql.connector import errorcode, conversion

from datetime import date
from os import path

import pandas as pd


class NumpyMySQLConverter(conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        return float(value)

    def _float64_to_mysql(self, value):
        return float(value)

    def _int32_to_mysql(self, value):
        return int(value)

    def _int64_to_mysql(self, value):
        return int(value)


class DBConnector:
    

    def __init__(self, user, password, database='mesomat', host='localhost'):  
        """
        
        Assigns config parameters and initializes commonly used commands    
        
        ---
        
        @parameter: user, str     
            username for the database, your mesomat email
        
        @parameter: password, str   
            password for the database
        
        @parameter: database, str       
            database to connect to
        
        @parameter: host, str
            name of the database host, e.g "localhost"
        
        """    
            
        
        self.config = {
            'user' : user,
            'password' : password,
            'host' : host,
            'database' : database,
            'raise_on_warnings' : True,
            'auth_plugin' : 'mysql_native_password'
            }
        
        self.INSERT_SAMPLE_COLUMN_COMMAND = ()
        
    
        self.connected = False
        self.cursor = None
        self.cnx = None
    
    def connect(self, verbose = True):      
        """
        
        Connect to the database. This function must be called before any 
        other function is called.   
        
        ---                
                
        @parameter: verbose, boolean  
            this function will print to the console if this is True
                
        """    
        try:
            
            self.cnx = mysql.connect(**self.config)
            self.cnx.set_converter_class(NumpyMySQLConverter)
            self.cursor = self.cnx.cursor()
            
            self.cursor.execute("SET GLOBAL max_allowed_packet=100*1024*1024") # max allowed file size = 100 MB
            
            self.connected = True
            
            if verbose: print("Connected to database.")
            
        except mysql.ProgrammingError as err:
            
            if (err.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                raise AuthenticationError
                
            else:
                raise
                
                
     
    def disconnect(self, verbose=True):            
        """        
        
        Connect to the database. This function must be called in order to 
        close the connection.      
        
        ----
                
        @parameter: verbose, boolean  
            this function will print to the console if this is True       
        """   
        self. cursor.close()
        self.cnx.close()
        
        self.connected = False
        
        if verbose: print("Disconnected from database.")
            
        
        
    
        
    def validate_action(self, message="This action may delete data from the database. This action cannot be undone.\nDo you wish to continue? (Y/N): "):
        """
        
        Prints an 'Are you sure?' message to the screen before any action that 
        could delete data.
        
        ---
        
        @return: boolean 
            True if the action it to be done, false if not
        
        """
        
        while True:
            print('\n\n')
            inp =  input(message)
            
            if (inp.upper() == 'Y'):
                return True
            elif (inp.upper() == 'N'):
                return False
        
            print("Invalid input. Try again")
        
        
        
    def add_sample(self, label, description='', material='', length=0.0, encased_in='', smpl_type='', imgpath='', fibreId=None, date_created='', verbose = True):        
            
        """
                
        Add new sample objects to the database
                
        ---
        
        @parameter: label, str        
            sample label, required, no newlines
    
        @parameter: description, str     
            sample description
    
        @parameter: material, str
            substrate material, no newlines e.g. "Carbon Fibre", "Acrylic"
        
        @parameter: length, float   
            length of sample, cm
        
        @parameter: encased_in, str
            epoxy, no newlines, e.g. "Mold Max 20T"
        
        @parameter: smpl_type, str
            type of sample, no newlines, e.g. "Square", "Divider"
    
        @parameter: imgpath, str
            path to image
              
        @parameter: fibreId, id    
            id corresponding to the fibre used in this sample, int
    
        @parameter: date_created, str 
            string in the form "yyyy-mm-dd", if null, today's date is used
                     
        @parameter: verbose, boolean  
            this function will print to the console if this is True
        """
        assert (self.connected)
        assert (type(label) == str)
        assert (type(description) == str)
        assert (type(length) == float)        
        assert (type(smpl_type) == str)
        assert (type(imgpath) == str)
        assert (type(fibreId) == int or fibreId == None)
        assert (type(date_created) == str)
        assert ('\n' not in label)
        assert ('\n' not in material)
        assert ('\n' not in encased_in)
        
        ADD_SAMPLE_COMMAND = ("INSERT INTO samples "
                              "(label, description, material, length, encased_in, type, img, img_size, fibreId, date_created) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ")
        
        img = None
        img_size = 0
        if (imgpath != ''):
            img = open(imgpath, 'rb').read()
            img_size = path.getsize(imgpath)
            if verbose: print("File uploaded: " + str(img_size / 1000.0) + " KB")
            
        

        if (date_created == ''):
            date_created = date.today().strftime("%Y-%m-%d")
        
        new_sample = (label, description, material, length, encased_in, smpl_type, img, img_size, fibreId, date_created)        
        
        self.cursor.execute(ADD_SAMPLE_COMMAND, new_sample)
            
        self.cnx.commit()
        
        if verbose: print("Sample added successfully")

        return self.cursor.lastrowid
    
    

    def add_data(self, label, description='', datapath='', samples=[], fibres=[], data_type='', date_created='', verbose = True):
        """
        
        Add new data objects to the database
        
        ---
        
        @parameter: label, str   
            data label, required, no newlines
                    
        @parameter: description, str   
            description of the test
        
        @parameter: datapath, str    
            path to .csv file
        
        @parameter: samples, list    
            list of strings (or list of ints), labels (or ids) of the samples 
            associated with this data object, max length = 4
                                    
        @parameter: fibres, list
            list of strings (or list of ints), labels (or ids) of the fibres 
            associated with this data object, max length = 2
                                    
        @parameter: date_created, str
            string in the form "yyyy-mm-dd", if null, today's date is used
                                                                        
        @parameter: verbose, boolean
            this function will print to the console if this is True
        """
        assert (self.connected)
        assert(type(label) == str)
        assert(type(datapath) == str)
        assert(type(samples) == list and len(samples) <= 4)
        assert(type(fibres) == list and len(fibres) <= 2)
        assert(type(date_created) == str)
        assert('\n' not in label)
        assert(len(samples) <= 4)
        assert(len(fibres) <= 2)
        
        
        ADD_DATA_COMMAND   = ("INSERT INTO data "
                              "(label,description, type, data, data_size, data_duration, data_numpoints, sampleId, sampleId2, sampleId3, sampleId4, fibreId, fibreId2, date_created) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        # get binary data from the file path specified
        data = None
        data_size = 0
        num_data_points = 0
        duration = 0      
        if (datapath != ''):
            data = open(datapath, 'rb').read()
            data_size = path.getsize(datapath)
            if verbose: print("File uploaded: " + str(data_size / 1000.0) + " KB")
            
            # get metadata from .csv file
            df = pd.read_csv(datapath)
            num_data_points = len(df)     
            if (len(df) > 0):
                if ('time' in df or 'Time' in df):                
                    duration = df['Time'].values[len(df)-1]
                else:
                    duration = -1   
            
        # fill in today's date,if none was given
        if (date_created == ''):
            date_created = date.today().strftime("%Y-%m-%d")
            
        # Get sample ids 
        sampleIds = []
        if (len(samples)>0 and type(samples[0]) == str):
            for s in samples:
                theId = self.get_by_label(s, 'samples')
                sampleIds.append(None if theId==-1 else theId )
        elif (len(samples)>0 and type(samples[0]) == int):
            sampleIds = samples
        # Ensure sample id list if exactly 4 items long
        sampleIds = [ sampleIds[i] if i<len(sampleIds) else None for i in range(4)]
            
            
        # get fibre ids
        fibreIds = []
        if (len(fibres)>0 and type(fibres[0]) == str):
            for f in fibres:
                theId = self.get_by_label(f, 'fibres')
                fibreIds.append(None if theId==-1 else theId )
        if (len(fibres)>0 and type(fibres[0]) == int):
            fibreIds = fibres
        # Ensure fibre id list if exactly 2 items long
        fibreIds = [ fibreIds[i] if i<len(fibreIds) else None for i in range(2)]
                            
        
        new_data = (label, description, data_type, data, data_size, duration, num_data_points, sampleIds[0], sampleIds[1], sampleIds[2], sampleIds[3], fibreIds[0], fibreIds[1], date_created)
        
        
        
        self.cursor.execute(ADD_DATA_COMMAND, new_data)
            
        self.cnx.commit()
        
        
        if verbose: print("Data added successfully")
        
        
    
    def add_fibre(self,  verbose = True):
        assert (self.connected)
        
        ADD_FIBRE_COMMAND  = ("INSERT INTO fibres "
                              "(label, material, coating, length, num_filament, winds_per_cm, heat_anneal, fabrication_notes, test_plate_notes, fibre_tester_notes, date_created) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        # TODO
        
        if verbose: print("Fibre added successfully")
    
    def add_plot(self, label, imgpath, samples=[], fibres=[], dataId=[], date_created='', verbose = True):
        assert (self.connected)        
        assert(type(label) == str)
        assert(type(imgpath) == str)
        assert(type(samples) == list and len(samples) <= 4)
        assert(type(fibres) == list and len(fibres) <= 1)
        assert(type(dataId) == list and len(dataId) <= 2)
        assert(type(date_created) == str)
        assert('\n' not in label)
        
        
        ADD_PLOT_COMMAND   = ("INSERT INTO plots"
                              "(label, img, img_size, date_created, dataId, dataId2, fibreId, sampleId, sampleId2, sampleId3, sampleId4) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ")
        
        # get binary data from the file path specified
        data = None
        data_size = 0

        if (imgpath != ''):
            data = open(imgpath, 'rb').read()
            data_size = path.getsize(imgpath)
            if verbose: print("File uploaded: " + str(data_size / 1000.0) + " KB")
                    
            
        # Get sample ids 
        sampleIds = []
        if (len(samples)>0 and type(samples[0]) == str):
            for s in samples:
                theId = self.get_by_label(s, 'samples')
                sampleIds.append(None if theId==-1 else theId )
        elif (len(samples)>0 and type(samples[0]) == int):
            sampleIds = samples
        # Ensure sample id list if exactly 4 items long
        sampleIds = [ sampleIds[i] if i<len(sampleIds) else None for i in range(4)]
            
            
        # get fibre ids
        fibreIds = []
        if (len(fibres)>0 and type(fibres[0]) == str):
            for f in fibres:
                theId = self.get_by_label(f, 'fibres')
                fibreIds.append(None if theId==-1 else theId )
        if (len(fibres)>0 and type(fibres[0]) == int):
            fibreIds = fibres
        # Ensure fibre id list if exactly 2 items long
        fibreIds = [ fibreIds[i] if i<len(fibreIds) else None for i in range(1)]
        
        # get data ids
        dataIds = []
        if (len(dataId)>0 and type(dataId[0]) == str):
            for f in dataId:
                theId = self.get_by_label(f, 'data')
                dataIds.append(None if theId==-1 else theId )
        if (len(dataId)>0 and type(dataId[0]) == int):
            dataIds = dataId            
        # Ensure fibre id list if exactly 1 items long
        dataIds = [ dataIds[i] if i<len(dataIds) else None for i in range(2)]
                
        # fill in today's date,if none was given
        if (date_created == ''):
            date_created = date.today().strftime("%Y-%m-%d")
            
        new_plot = (label, data, data_size, date_created, dataIds[0], dataIds[1], fibreIds[0], sampleIds[0], sampleIds[1], sampleIds[2], sampleIds[3])        
        
        
        self.cursor.execute(ADD_PLOT_COMMAND, new_plot)
            
        self.cnx.commit()
        
          
        
        if verbose: print("Plot added successfully")
    

    def insert_column(self, column_name, column_type, table, params=None, overwrite=False, after_col=None, verbose=True):        
        """
    
        Adds the specified column to the specified table. 
    
        ---
                
        @parameter: column_name, str
            name of the column to added
    
        @parameter: column_type, str 
            type of the column, must be a SQL type
        
        @parameter: table, str
            the name of the table to add the column to. Must already exist in 
            the database
    
        @parameter: params, dict  
            SQL parameters
                                        
        @parameter: overwrite, boolean
            If True: if the column already exists but is  of a different type, 
            the existing column will be deleted and a new column will be created.
            
            If False: if the column already exists, this function does nothing
                                    
        @parameter: after_col, str
            Name of the column after which to insert the column specified by 
            'column_name'
        
        @parameter: verbose, boolean       
            this function will print to the console if this is True  
        
        """
        
        assert(self.connected)
        
        try: assert(self.check_table(table, verbose=False)) 
        except AssertionError: raise TableNotFoundError
            
                    
            
        if self.check_column(column_name, table, verbose=False):     
            
            if not overwrite:
                                
                    if verbose: print("The column '{0}' already exists in the table '{1}'.".format(column_name, table))
                    return False
                    
            else:
                
                if verbose: 
                    print("The column '{0}' already exists in the table '{1}'.".format(column_name, table))
                    
                self.delete_column(column_name,table,verbose=True)
                    
                self._insert_column(column_name, column_type, table, params, overwrite, after_col)
                
        else:
          
            self._insert_column(column_name, column_type, table, params, overwrite, after_col)
            
           
        if verbose: print("Column '{0}' added to the table '{1}' successfully.".format(column_name, table))
        
        return True
    

    def _insert_column(self, column_name, column_type, table, params=None, overwrite=False, after_col=None, verbose=True):
        
        """
        
        Private helper function used in self.insert_column(). Do not call this function
        outside of this class
        
        ---
                
        @parameter: column_name, str
            name of the column to added
    
        @parameter: column_type, str 
            type of the column, must be a SQL type
        
        @parameter: table, str
            the name of the table to add the column to. Must already exist in 
            the database
    
        @parameter: params, dict  
            SQL parameters
                                        
        @parameter: overwrite, boolean
            If True: if the column already exists but is  of a different type, 
            the existing column will be deleted and a new column will be created.
            
            If False: if the column already exists, this function does nothing
                                    
        @parameter: after_col, str
            Name of the column after which to insert the column specified by 
            'column_name'
        
        @parameter: verbose, boolean       
            this function will print to the console if this is True  
        
        """
          
        not_null = ''
        auto_increment = ''
                
        if params != None and 'not_null' in params:
            not_null = 'NOT NULL'
        
            
        if params != None and 'auto_increment' in params:
            auto_increment = "AUTO_INCREMENT"
        
        
        ADD_COLUMN_COMMAND = "ALTER TABLE {0} ADD {1} {2} {3} {4}".format(table, column_name, column_type, not_null, auto_increment)
    
        if (after_col != None and type(after_col) is str):
            ADD_COLUMN_COMMAND += " AFTER {0} ".format(after_col)
        
        
        self.cursor.execute(ADD_COLUMN_COMMAND)
     
        if verbose: 
            print("Adding the column '{0}' to the table '{1}'...".format(column_name, table))
            print("\t" + ADD_COLUMN_COMMAND)    
        
    
        if params != None and 'foreign_key' in params:
            
            if 'references' not in params:
                raise InvalidParameterError
            
            referenced_table = params['references'].split('(')[0]
            referenced_column = params['references'].split('(')[1][:-1]            
            
            
            if (not self.check_table(referenced_table, verbose=False)):
                raise(TableNotFoundError)
                
                 
            if (not self.check_column(referenced_column, referenced_table, verbose=False)):
                raise(ColumnNotFoundError)
                
                
            ADD_FOREIGN_KEY_COMMAND = "ALTER TABLE {0} ADD FOREIGN KEY ({1}) REFERENCES {2}({3})".format(table, column_name, referenced_table, referenced_column)
            
                    
            if verbose: 
                print("\t" + ADD_FOREIGN_KEY_COMMAND)    
                
            self.cursor.execute(ADD_FOREIGN_KEY_COMMAND)
            
            
    def clear_column(self, column_name, table, validate=True, verbose=True):    
        """
        
        Removes all data from the specified column. 
        
        WARNING: THIS ACTION CANNOT BE UNDONE
        
        ---
        
        @parameter: column_name, str
            name of the column to cleared
        
        @parameter: table, str 
            the name of the table containing the specified column. Must already
            exist in the database            
                                    
        @parameter: validate, boolean
            If true, this function will ask for user input before deleting any data
            from the database                            
                                    
        @parameter: verbose, boolean       
            this function will print to the console if this is True  
        
        @return: boolean
            True if the column was successfully cleared, False if not         
        
        """
        assert(self.connected)
        
        try: assert(self.check_table(table, verbose=False)) 
        except AssertionError: raise TableNotFoundError
            
        try: assert(self.check_column(column_name, table, verbose=False))
        except AssertionError: raise ColumnNotFoundError
        
        if validate: 
            if not self.validate_action(): return False  # ask for user input before proceeding    
        
        CLEAR_COLUMN_COMMAND = "UPDATE {0} SET {1} = NULL ".format(table,column_name)
                
        self.cursor.execute(CLEAR_COLUMN_COMMAND)        
        
        return True
            
    

    def delete_column(self, column_name, table, validate=True, verbose=True):    
        """
        
        Deletes the column specified by 'column_name' from the table specified
        by 'table_table'. Returns True if the column was found and successfully
        deleted, False if not.
        
        ---
        
        @parameter: column_name, str
            name of the column to deleted
        
        @parameter: table, str
            the name of the table to delete the column from. Must already exist i
            n the database
                                    
        @parameter: validate, boolean
            If true, this function will ask for user input before deleting any data
            from the database                            
                                    
        @parameter: verbose, boolean       
            this function will print to the console if this is True  
               
        @return: boolean
            True if the column is successfully deleted, False if not                  
        """         
        assert(self.connected)
        
        try: assert(self.check_table(table, verbose=False)) 
        except AssertionError: raise TableNotFoundError
            
        try: assert(self.check_column(column_name, table, verbose=False))
        except AssertionError: raise ColumnNotFoundError
            
        
        GET_SCHEMA_FK_INFORMATION_COMMAND   = "SELECT COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME " \
                                              "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE " \
                                              "WHERE REFERENCED_TABLE_SCHEMA = '{0}'  AND TABLE_NAME = '{1}' AND COLUMN_NAME = '{2}'"
                                              
        DROP_COLUMN_COMMAND                 = "ALTER TABLE {0} DROP {1}".format(table, column_name)
        
        DROP_FK_CONSTRAINT_COMMAND          = "ALTER TABLE {0} DROP FOREIGN KEY {1}" 
        
        
        if validate: 
            if not self.validate_action(): return False
        
        # check if column has a foreign key constraint
        
        cmd = GET_SCHEMA_FK_INFORMATION_COMMAND.format(self.config['database'], table, column_name)
        
        self.cursor.execute(cmd)
        
        fk_name = None
        for row in self.cursor:
            fk_name = row[1]
            break
        
        if fk_name != None:
            cmd = DROP_FK_CONSTRAINT_COMMAND.format(table, fk_name)
            
            if verbose: 
                print("Column '{0}' involved in foreign key constraint '{1}'".format(column_name, fk_name))
                print("Dropping foreign key constraint '{0}'".format(fk_name))
                print("\t" + cmd)
                
            self.cursor.execute(cmd)

            
                
        if verbose:
            print("Dropping the column '{0}' from the table '{1}'...".format(column_name, table))
            print("\t" + DROP_COLUMN_COMMAND)
                    
        self.cursor.execute(DROP_COLUMN_COMMAND)
            
        return True
        
        
        

    def check_column(self, column_name, table, verbose=True):
        """
        
        Returns True if the specified column exists in the table
                
        ---
        
        @parameter: column_name, str
            name of the column to be checked
        
        @parameter: table, str 
            the name of the table containing the specified column
        
        @parameter: verbose, boolean         
            this function will print to the console if this is True
            
        @return: boolean
            True if the column exists in the table, False if not
        """  
        assert(self.connected)
        try: 
            assert(self.check_table(table, verbose=False)) 
        except AssertionError: 
            raise TableNotFoundError
            
            
        CHECK_COLUMN_COMMAND = "SHOW COLUMNS FROM {0} LIKE '{1}'".format(table, column_name)
        
        self.cursor.execute(CHECK_COLUMN_COMMAND)
        
        exists=False
        for row in self.cursor:
            exists = True
            break
        
        if verbose and exists: print("Column with label '{0}' found in table '{1}'".format(column_name, table))
        elif verbose: print("Column with label '{0}' not found in table '{1}'".format(column_name, table))            
        
        return exists
    

    def get_column_information(self, column_name, table, verbose=True):
        """        
        
        Returns dictionary with information on the specified column
    
        ---    
        
        @parameter: column_name, str
            name of the column to be checked
        
        @parameter: table, str      
            the name of the table containing the specified column
        
        @parameter: verbose, boolean
            this function will print to the console if this is True
                                    
        @return: dict
            a dictionary in the form
                            
        """  
        
        assert(self.connected)
        try: 
            assert(self.check_table(table, verbose=False)) 
        except AssertionError: 
            raise TableNotFoundError
            
        if (not self.check_column(column_name, table, verbose=False)):
            return
            
        GET_COLUMN_INFO_COMMAND = ("SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA "
                            		"FROM INFORMATION_SCHEMA.COLUMNS "
                            		"WHERE TABLE_NAME='{0}' and COLUMN_NAME = '{1}'".format(table,column_name))
        
        self.cursor.execute(GET_COLUMN_INFO_COMMAND)
  
        for row in self.cursor:
            break
        
        info = {'type' : row[0],
                'not_null' : row[1] != 'YES' , 
                'foreign_key' : row[2] == 'MUL',
                'auto_incremenet' : row[3] == 'auto_increment'}
        
        if verbose: print("Column with label '{0}' found in table '{1}'".format(column_name, table))
        
    
        return info
    
    
    
    
        

    def check_table(self, table, verbose=True):    
        """        
        
        Returns True if the specified table exists in the database
        
        ---
        
        @parameter: table, str
            the name of the table to check
        
        @parameter: verbose, boolean      
            this function will print to the console if this is True
                                    
        @return: boolean
            True if the table exists in the database, False if not
            
        """    
        
        assert(self.connected)

        CHECK_TABLE_COMMAND = "SHOW TABLES LIKE '{0}'".format(table)
        
        
        self.cursor.execute(CHECK_TABLE_COMMAND)
        
        exists = False
        for row in self.cursor:
            exists = True
            break
               
        if verbose and exists: print("Table with name '{0}' found.".format(table))
        elif verbose:  print("Table with name '{0}' not found.".format(table))
        
        return exists
    

    def validate_table(self, table, table_struct, verbose=True):
        """        
        
        Looks through table structure and ensures all columns appear with the
        specified name, type and parameters.
        
        ---
                
        @parameter: table, str      
            the name of the table to validate
        
        @parameter: table_struct, dict
            dictionary with the column name as the key and with a list of 
            form ("type", params) as the value
                                    
        @parameter: verbose, boolean
            this function will print to the console if this is True
                                                        
        @return: boolean                    
            True if the validation completed successfully, False if not.
        """
        
        assert(self.connected)
        try: 
            assert(self.check_table(table, verbose=False)) 
        except AssertionError: 
            raise TableNotFoundError
        
        GET_SCHEMA_INFORMATION_COMMAND      = "SELECT ORDINAL_POSITION, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA " \
                                          	  "FROM INFORMATION_SCHEMA.COLUMNS " \
                                          	  "WHERE TABLE_NAME='{0}' ORDER BY ORDINAL_POSITION".format(table)
        
        GET_SCHEMA_FK_INFORMATION_COMMAND   = "SELECT COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME " \
                                              "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE " \
                                              "WHERE REFERENCED_TABLE_SCHEMA = '{0}'  AND TABLE_NAME = '{1}' AND COLUMN_NAME = '{2}'"
                                              
        CHANGE_TYPE_COMMAND                 = "ALTER TABLE {0} MODIFY {1} {2} {3}"
                                           
        ADD_FK_COMMAND                      = "ALTER TABLE {0} ADD FOREIGN KEY ({1}) REFERENCES {2}({3})"                
                       
        DROP_FK_CONSTRAINT_COMMAND          = "ALTER TABLE {0} DROP FOREIGN KEY {1}" 
        
        
        self.cursor.execute(GET_SCHEMA_INFORMATION_COMMAND)
        
        # load all column info from the database 
        columns = {}
        for c in self.cursor:
            columns[c[1]] = c
                    
        for column,db_col in zip(table_struct,columns):
            
            # load parameter values from the DB 
            (ord_pos, name, col_type, isnull, key_type, extra) = columns[db_col]
            
            isnull = isnull == 'YES'
            auto_increment = extra == 'auto_increment'
            foreign_key = key_type == 'MUL'
            
            # parse new parameter values
            struct_type = table_struct[column][0]
            parameters = table_struct[column][1] if ( len(table_struct[column]) > 1) else None
            
            # get parameters values in boolean format
            if (parameters == None):
                new_isnull = True
                new_auto_increment = False
                new_foreign_key = False
            else:
                if 'not_null' in parameters: new_isnull = not parameters['not_null']
                else: new_isnull  = True
                    
                if 'auto_increment' in parameters: new_auto_increment = parameters['auto_increment']
                else: new_auto_increment = False
                    
                if 'foreign_key' in parameters: new_foreign_key = parameters['foreign_key']
                else: new_foreign_key = False
            
            
            
            
            if verbose: 
                print("\n---\n\nChecking column '{0}'...".format(column))
                
            # check name, type and each parameter    
            if name == column:
                
                # if something doesn't match, change within the database
                if ( col_type != struct_type ):                                    
                   if verbose:
                       print("Column '{0}' found in the correct position with the incorrect type.".format(column))
                       print("Changing the type of '{0}' from '{1}' to '{2}'".format(column, col_type, struct_type),)
                       
                   cmd = CHANGE_TYPE_COMMAND.format(table, column, struct_type.upper(), '')
                   
                   if verbose: print("\t" + cmd)
                   
                   self.cursor.execute(cmd)                
                
                if ( isnull != new_isnull ):
                                               
                   if verbose:
                       print("Column '{0}' found in the correct position an incorrect parameter.".format(column))
                       print("Changing the type of '{0}' from '{1}' to '{2}'".format(column, "NOT NULLABLE" if new_isnull else "NULLABLE",  "NULLABLE" if new_isnull else "NOT NULLABLE"))
                       
                             
                   cmd = CHANGE_TYPE_COMMAND.format(table, column, struct_type.upper(), "NOT NULL" if not new_isnull else "" )
                   
                   if verbose: print("\t" + cmd)
                   
                   
                   self.cursor.execute(cmd)
                   
                if ( auto_increment != new_auto_increment ):
                                               
                   if verbose:
                       print("Column '{0}' found in the correct position an incorrect parameter.".format(column))
                       print("Changing the type of '{0}' from '{1}' to '{2}'".format(column, "AUTO INCREMENT" if new_auto_increment else "none",  "none" if new_auto_increment else "AUTO INCREMENT"))
                       
                             
                   cmd = CHANGE_TYPE_COMMAND.format(table, column, struct_type.upper(), "AUTO INCREMENT" if new_auto_increment else "" )
                   
                   if verbose: print("\t" + cmd)
                   
                   
                   self.cursor.execute(cmd)
               
                
                if ( foreign_key != new_foreign_key ):
                    
                                                              
                    if verbose:
                        print("Column '{0}' found in the correct position an incorrect parameter.".format(column))
                        print("Changing the type of '{0}' from '{1}' to '{2}'".format(column, "FOREIGN KEY" if new_auto_increment else "none",  "none" if new_auto_increment else "FOREIGN KEY"))
                       
                             
                    
                    if ('foreign_key' in parameters and parameters['foreign_key']):
                                   
                        referenced_table = parameters['references'].split('(')[0]
                        referenced_column = parameters['references'].split('(')[1][:-1]            
    
    
                        if (not self.check_table(referenced_table, verbose=False)):
                            raise(TableNotFoundError)
    
     
                        if (not self.check_column(referenced_column, referenced_table, verbose=False)):
                            raise(ColumnNotFoundError)
    
                
                        cmd = ADD_FK_COMMAND.format(table,column,referenced_table, referenced_column)

                            
                            
                        if verbose: print("\t" + cmd)
                        
                        try:
                            self.cursor.execute(cmd)                       
                        except:
                            print("      > Error: Cannot add foreign key constraint to column '{0}' in the table '{1}'. You must remove all data from\n      > this column using the clear_column() command first.".format(column, table))
                   
                    else:
                        
                        # check if column has a foreign key constraint
                        
                        cmd = GET_SCHEMA_FK_INFORMATION_COMMAND.format(self.config['database'], table, column)
                        
                        self.cursor.execute(cmd)
                        
                        fk_name = None
                        for row in self.cursor:
                            fk_name = row[1]
                            break
                        
                        if fk_name != None:
                            cmd = DROP_FK_CONSTRAINT_COMMAND.format(table, fk_name)
                            
                            if verbose: 
                                print("Column '{0}' involved in foreign key constraint '{1}'".format(column, fk_name))
                                print("Dropping foreign key constraint '{0}'".format(fk_name))
                                print("\t" + cmd)
                                
                            self.cursor.execute(cmd)

                   
                
                if verbose: print("Done.")
                   
            
        if (len(columns) > len(table_struct)):
            
            if verbose: print("\n---\n\nExtra columns found in database")
            
            for col in columns:
                if (col not in table_struct):                  
                    
                    if verbose:
                       print("Column '{0}' found in the database but not found in the configuration.".format(col))
                                 
                    self.delete_column(col, table)
            
        
        elif(len(table_struct) > len(columns)):
            
            if verbose: print("\n---\n\nExtra columns found in configuration. ")

            for col in table_struct:
                if col not in columns:
                    if verbose: print("Column '{0}' found in configuration but not in database".format(col))
                    self.insert_column(col, table_struct[col][0], table, params =  table_struct[col][1] if ( len(table_struct[col]) > 1) else None)
                
            
            
    def create_table(self, table_name, table_struct, verbose=True ):
        """
                
        Loops through a table structure and adds each column with the specified
        parameters
        
        ---
        
        @parameter: table_name, str      
            name of the table
        
        @parameter: table_struct, str           
            structure describing each column in the table
                                    
        
        @parameter: verbose, boolean         
            this function will print to the console if this is True
                                    
        @return: boolean
            True if the table was successfully created, False if not
        """
        
    
        CREATE_TABLE_COMMAND    = "CREATE TABLE {0} ( " \
                                  "{1} {2} {3} {4}, " \
                                  "PRIMARY KEY ({1}) " \
                                  ");"
    
        # add the first column, since a table cannot be created unless it has 
        # at least one column
                                  
        for first_col in table_struct:
            col_type = table_struct[first_col][0]
            params = table_struct[first_col][1] 
            
            if 'primary_key' not in params or 'not_null' not in params or 'auto_increment' not in params:
                raise InvalidIdError
            if not params['primary_key'] or not params['not_null'] or not params['auto_increment']:
                raise InvalidIdError
                
            break
        
        not_null = ''
        auto_increment ='' 
        
        if params != None and 'not_null' in params:
            not_null = 'NOT NULL'
        
            
        if params != None and 'auto_increment' in params:
            auto_increment = "AUTO_INCREMENT"
            
        cmd = CREATE_TABLE_COMMAND.format(table_name, "id", col_type, not_null, auto_increment)
        
        if verbose: print("\t" + cmd)
        
        self.cursor.execute(cmd)
        
        
        
        # loop through the table struct and add the rest of the columns
        skip=True
        for col in table_struct:
            if (skip):
                skip=False
                continue
            col_type = table_struct[col][0]
            params = table_struct[col][1] 
            self.insert_column(col,col_type,table_name,params)
        
        
        
        
    def delete_table(self, table_name, validate=True, verbose=True):
        """
                
        Deletes the specified table from the database
                
        ---
        
        @parameter: table_name, str
            The name of the table to be deleted
        
        @parameter: validate, boolean
            If true, this function will ask for user input before deleting any data
            from the database                            
                                    
        @parameter: verbose, boolean       
            this function will print to the console if this is True         
            
        @return: boolean
            True if the table is successfully deleted, False if not
        """
        
        assert(self.connected)
        try: 
            assert(self.check_table(table_name, verbose=False)) 
        except AssertionError: 
            raise TableNotFoundError
        
        
        DELETE_TABLE_COMMAND = "DROP TABLE {0}".format( table_name)
        
        if validate: 
            if not self.validate_action(): return False
        
        if verbose: 
            print("Deleting the table '{0}' from the database '{1}'...".format(table_name, self.config['database']))
            print("\t" + DELETE_TABLE_COMMAND)
            
        self.cursor.execute(DELETE_TABLE_COMMAND)
        
        return True
        
        
    def get_table_names(self,verbose=False):
        """
                
        Returns a list of the existing tables in the database
                
        ---

        @parameter: verbose, boolean         
            this function will print to the console if this is True
                                    
        @return: list
            list of strings
        """
        
        assert(self.connected)
        
        
        GET_TABLE_NAMES_COMMAND = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{0}'".format(self.config['database'])
        
        self.cursor.execute(GET_TABLE_NAMES_COMMAND)
        
        tables = []
        for row in self.cursor:
            tables.append(row[0])
        
        return tables
        
        
        

    def get_by_label(self, label, table, verbose=True):
        """
                
        Returns the id of the item specified by 'label' in the table 
        specified by 'table'. If the item does not exist in the table,
        this function returns -1.
                
        ---
        
        @parameter: label, str      
            data label, required, no newlines
        
        @parameter: table, str           
            the table from which to retrieve the id from,
                                    
        
        @parameter: verbose, boolean         
            this function will print to the console if this is True
                                    
        @return: int
            the id of the item if it exists; if not, -1
        """
        assert (self.connected)
        
        theId = -1
        GET_BY_LABEL_COMMAND = "SELECT id,label FROM {0} WHERE samples.label = \"{1}\"".format(table, label)
        
        
        self.cursor.execute(GET_BY_LABEL_COMMAND)
        
        for row in self.cursor:
            theId = row[0]
            break
                
        if verbose and theId != -1: 
            print("Item with id {0} and label '{1}' retrieved.".format(theId, label))
        elif verbose:            
            print("No item in the table '{0}' with the label '{1}' was found.".format(table, label))
            
        return int(theId)