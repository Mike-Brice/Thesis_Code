"""
Program Title:
    save_Error.py
    
Author: 
    Mike Brice
    
Last Modified:
    Sat Sep 4, 2018

Description: 
    Saves an instance of an error into the Error_Log.db SQLite database.
    
    If the save_Error fails to log the error then the URL that is associated
    with the error will be lost. 
"""

# =============================================================================
# Imports
# =============================================================================
import sqlite3
import datetime
import time
import thread
import sys

# =============================================================================
# save_Error | Saves the current Error to the Error Log Database
# =============================================================================
'''
Function Parameters
    level - What Error Level the error was at
    text - Custom text describing the error
    URL - Current URL being downloaded
    message - Error message that would be displayed to the screen
'''
def save_Error(level, text, URL, message):
    
    wait = [5,10,30,60] # Seconds to wait for next attempt
    attempts = 0 # Initialize the attempts counter
    status = True # Sets the loop terminator to True
    
    while status:
        try:
            connection = sqlite3.connect("Error_Log.db")
            
            cursor = connection.cursor()
        
            time_now = datetime.datetime.now()
            date = time_now.strftime("%A %B %d, 20%y")
            tm = time_now.strftime("%I:%M %p")
            
            params = (level, date, tm, text, URL, message)
        
            cursor.execute("INSERT INTO Error (Key, Level, Date, Time, Text, URL, Message) VALUES (NULL,?,?,?,?,?,?)", params)
                
            connection.commit()
            connection.close()
            status = False
        
        except sqlite3.Error:
            print "SQLError: Attempting to insert error again in %d seconds" % (wait[attempts])
            time.sleep(wait[attempts])
            
            if attempts == 3:
                status = False
                print "Failed to log error"
                connection.rollback()

                thread.interrupt_main()
                sys.exit()
            attempts += 1  
            connection.rollback()