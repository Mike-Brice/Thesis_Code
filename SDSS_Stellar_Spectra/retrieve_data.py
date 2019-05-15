'''
Program Title: 
    retrieve_data.py

Author:
    Mike Brice
    
Last Modified:
    Fri Sep 14, 2018
    
Description:
    Retrieves data from the SDSS_Data.db database and converts the columns
    into their original types. For example Flux, Wavelengths, and Emission
    and Absorption Lines are stored in the database as unicode, so they are
    converted back into Numpy float arrays. 
    
'''
#==============================================================================
# Imports
#==============================================================================
import sqlite3

#from error_handling import retrieve_error
from SDSS_Stellar_Spectra.process_data import __process_data
from SDSS_Stellar_Spectra.process_data import __process_one

'''
# Used for the client server database | Under developement
from request import request_set
from request import request_all
from request import request_one
from request import request_class
'''

#==============================================================================
# retrieve_one
#==============================================================================
'''
Function Parameters:
    table - The table in the database you would like to query 
    column - Column that the identifier is associated with. 
    identifier - identifies the specific row 
    columns - Default to *, the columns to return from the database table
    database - Default to SDSS_Data.db, the database that the user wants to query
    
Function Returns:
    ret - Returns a tuple of data that was retrieved from the database table
          that are processed into their appropriate types
'''
def retrieve_one(table, column, identifier, columns = "*", database = "SDSS_Data.db"):
    
    try:
        connection = sqlite3.connect(database) # Connects to the database
                
        cursor = connection.cursor() # Makes a cursor to go throug the database
           
        # Gets all of the columns from the table at the particular Column and Identifier
        cursor.execute("SELECT %s FROM %s WHERE %s Like %s" % (columns, table, column, identifier)) 
        ret = cursor.fetchone() 
        
        connection.close() # Close the database connection

        if ret == None:
            print ("Identifier out of bounds")
            return None
        
        return __process_one(ret)
    
    except sqlite3.Error:
        #retrieve_error()
        
        return None

#==============================================================================
# retrieve_all
#==============================================================================
''' 
Function Parameters:
    table - The table in the database you would like to query 
    columns - Default to *, the columns to return from the database table
    database - Default to SDSS_Data.db, the database that the user wants to query
    
Function Returns:
    ret - Returns the list of data that was retrieved from the database table
          that are processed into their appropriate types
'''
def retrieve_all(table, columns = "*", database = "SDSS_Data.db"):
    
    try:
        connection = sqlite3.connect(database) # Connects to the database
                
        cursor = connection.cursor() # Makes a cursor to go throug the database
        
        cursor.execute("SELECT %s FROM %s" % (columns, table)) 
        ret = cursor.fetchall()
        
        connection.close() # Close the database connection
        
        if not ret:
            print ("Identifier out of bounds")
            return None
        return __process_data(ret)
    
    except sqlite3.Error:
        #retrieve_error()
        
        return None

#==============================================================================
# retrieve_group
#==============================================================================
'''
Function Parameters:
    table - The table in the database you would like to query 
    cls   - The class that you want to retrieve.
    columns - Default to *, the columns to return from the database table
    database - Default to SDSS_Data.db, the database that the user wants to query
    
Function Returns:
    ret - Returns the list of data that was retrieved from the database table
          that are processed into their appropriate types
'''
def retrieve_class(table, cls, columns = "*", database = "/home/mike/Documents/SDSS_Data.db"):
    
    try:
        connection = sqlite3.connect(database) # Connects to the database
                
        cursor = connection.cursor() # Makes a cursor to go throug the database
        
        cursor.execute("SELECT %s FROM %s WHERE Class Like %s" % (columns, table, cls)) 
        ret = cursor.fetchall()
        
        connection.close() # Close the database connection
        
        if not ret:
            index = cls.find('%') # Finds the first instance of %
            
            if index > 2 or index == -1:
                index = 0
                
            index2 = cls.rfind('%') # Finds the last instance of %
            if index2 == -1 or index2 == 1:
                index2 = cls.rfind('\'')
            
            print ("%s is not a valid class" % cls[index+1:index2])
            
            return None
        
        return __process_data(ret)
    
    except sqlite3.Error:
        #retrieve_error()
        
        return None
    
#==============================================================================
# retrieve_set
#==============================================================================
'''
Function Parameters:
    table - The table in the database you would like to query 
    amount - The number of rows to be retrieved from the database
    offset - Default to 0, starting row in the table to be retrieved 
    columns - Default to *, the columns to return from the database table
    database - Default to SDSS_Data.db, the database that the user wants to query
    
Function Returns:
    ret - Returns the list of data that was retrieved from the database table
          that are processed into their appropriate types
'''
def retrieve_set(table, amount, offset = 0, columns = "*", database = "/home/mike/Documents/SDSS_Data.db", print_Error = True):
    
    if amount < 2:
        print ("Amount needs to be 2 or greater")
        return None
    
    else:
        try:
            connection = sqlite3.connect(database) # Connects to the database
                    
            cursor = connection.cursor() # Makes a cursor to go throug the database
            
            cursor.execute("SELECT %s FROM %s LIMIT %d OFFSET %d" % (columns, table, amount, offset))
            
            ret = cursor.fetchall()
            
            connection.close() # Close the database connection
            
            if not ret:
                if not print_Error:
                    #print ("Identifier out of bounds")
                    pass
                return None
            
            return __process_data(ret)
        
        except sqlite3.Error:
            #retrieve_error()
            
            return None
        