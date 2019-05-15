"""
Program Title:
    workerThread.py
    
Author: 
    Mike Brice
    
Last Modified:
    Sat Sep 4, 2018

Description: 
    Creates a thread that performs the work of the program. This thread 
    downloads and gets the data out of the .FITs files. It then inserts the
    data into the database and then terminates. 
    
    This thread is used to ensure safe shutdown of the program. If the 
    KeyboardInterrupt is flagged then this thread is allowed to finish before 
    shutdown of the program. 
    
    A single thread is created, works on a single URL / .FITs file, then
    terminates. A new thread is created for the next single URL / .FITs file.
"""

# =============================================================================
# Imports
# =============================================================================
import urllib
import threading
import os

from error_handling import error_handling as error_handling
from get_Data import get_Data as get_Data
from append_Database import append_Database as append_Database

# =============================================================================
# Worker Thread that extracts and inserts the data
# =============================================================================
class workerThread (threading.Thread):
    
    # =========================================================================
    # Constructor
    # =========================================================================
    def __init__(self, current_URL, database):
        threading.Thread.__init__(self)
        self.current_URL = current_URL
        self.database = database
    
    # =========================================================================
    # Runs the thread
    # =========================================================================
    def run(self):
            
        current_URL = self.current_URL # Initializes current_URL
        
        index = current_URL.rfind('/') # Finds the last instance of /
        index2 = current_URL.find('\r') # Finds the firstinstance of \r
        fileName = current_URL[index+1:index2:] # Extracts the file name out of the URL
        
        # Prints File Name to screen
        #print "File Name: %s" % (fileName)
        
        downloadFile = urllib.URLopener() # Creates an instance of URLopener
        
        error_handling("connect to SDSS servers","connect to SDSS server", "\nError Level 3\nURL at failure: %s" % (current_URL), 
                       3, downloadFile.retrieve, current_URL, fileName) # Downloads the file
        
        wavelength, model, cls, lines, Z, Z_ERR = get_Data(fileName, current_URL) # Gets the data from the file
        
        try:
            index = cls.index("(")
            cls = cls[:index-1]
        except ValueError:
            pass
        
        major = ["O", "B", "A", "F", "G", "K", "M"]
        minor = [9,8,7,6,5,4,3,2,1,0]
        mk = ["I", "II", "III", "IV", "V", "VI"]
        
        valid = False
        
        for ma in major:
            for mi in minor:
                for m in mk:
                    if cls == (ma+str(mi)+m):
                        valid = True
                        break
                else:
                    continue
                
                break
            else:
                continue
            
            break
        
        if valid and len(model) >= 3800:
            
            # Formats for insertion
            model = map(float, model)
            wavelength = map(float, wavelength)
            lines = map(float, lines)
            
            append_Database(True, current_URL, fileName, cls, model, wavelength, lines, Z, Z_ERR, None, self.database)
            
        # If the class is not a valid class add File Name to the rejected list
        else:
            
            if len(model) < 3800:
                reason = "To few flux measurements"
            else:
                reason = "Invalid Class"
            
            #print "Rejected, Class: %s, Reason: %s" % (cls, reason)
            
            append_Database(False, current_URL, fileName, cls, None, None, None, None, None, reason, self.database)
        
        # If the current spectra .FITS file exists, delete it
        error_handling("delete .FITs file", "delete .FITs file", current_URL, 1, os.remove, fileName)
        
        #print ""
