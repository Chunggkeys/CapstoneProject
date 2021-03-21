# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 12:20:01 2020



@author: Alexander
"""

        
class AuthenticationError(Exception):
    def __str__(self):
        return "Invalid username or password when connecting to database."

class TableNotFoundError(Exception):
    def __str__(self):
        return "The specified table was not found in the database."

class ColumnNotFoundError(Exception):
    def __str__(self):
        return "The specified column was not found in the table."

class InvalidParameterError(Exception):
    def __str__(self):
        return "The parameters used for adding or editing a column are not correct."
    
class InvalidIdError(Exception):
    def __str__(self):
        return "The first column in a new table must have the parameters 'primary_key', 'not_null' and 'auto_increment' set to True."
