"""
Program Title:
    append_Database.py
    
Author: 
    Mike Brice
    
Last Modified:
    Sat Sep 4, 2018

Description: 
    This appends the SDSS_Data.db SQLite database. 
    
    If inserting into the database fails, then the program will attempt
    4 times to insert the data. If the program fails by the end of the 4th
    attempt then the error is logged and the program continues on.
"""

# =============================================================================
# Imports
# =============================================================================
import datetime
import sqlite3
import time

from save_Error import save_Error as save_Error

# =============================================================================
# append_Database | appends into either the Accepted or Rejected tables
# =============================================================================
'''
Function Parameters
    table - True = Accepted, False = Rejected
    URL - Current URL that is being downloaded
    fileName - The file name of the spectra being inserted
    cls - Class of the star
    flux - Array of flux data
    wavelength - Float array of wavelength data in logoritmic form
    EALines - Emission and Absorption lines
'''
def append_Database(table, URL, fileName, cls, flux, wavelength, EALines, Z, Z_ERR, reason, database):
    
    wait = [5,10,30,60] # Seconds to wait for next attempt
    attempts = 0 # Initialize the attempts counter
    status = True # Sets the loop terminator to True
    
    while status:
        try:
            connection = sqlite3.connect(database) # Connect to the database
            
            cursor = connection.cursor() # Creates a cursor
            
            time_now = datetime.datetime.now() # Gets the time of right now
            date = time_now.strftime("%A %B %d, 20%y") # Formats the date | Only works in the 20xx years
            
            # If table is set to True insert into the Accepted table
            if table:
                # Python variables stored to become SQLite variables
                params = (URL, fileName, cls, str(flux), str(wavelength), str(EALines), str(Z), str(Z_ERR), date) 
            
                # Inserts the data into the database
                cursor.execute("INSERT INTO Accepted (Key, URL, File_Name, Class, Flux, Wavelength, EALines, Z, Z_ERR, Date) VALUES (NULL,?,?,?,?,?,?,?,?,?)", params)
            
            # If table is set to False insert into the Rejected table
            else:
                # Python variables stored to become SQLite variables
                params = (URL, fileName, cls, reason, date)
                
                # Inserts the data into the database
                cursor.execute("INSERT INTO Rejected (Key, URL, File_Name, Class, Reason, Date) VALUES (NULL,?,?,?,?,?)", params)
                
            connection.commit() # Commits to the changes to the database
            connection.close() # Closes the connections
            status = False # Kill the error handler
        
        # If there is an error inserting the data
        except sqlite3.Error as e:
            print "SQLError: Attempting to insert data again in %d seconds" % (wait[attempts])
            time.sleep(wait[attempts])
            
            # If there were ~1 minute worth of attempts skip this spectra and move on
            if attempts == 3:
                status = False
                save_Error(1, "Failed to enter data into database", URL, str(e)) # Log the error
                print "Failed to insert data"
                
            attempts += 1 # Itterate the counter
            
            connection.rollback() # If an error occured rollback the changes to the database
        
        
    if attempts > 0 and attempts < 3:
        print "SQLError has been resolved"