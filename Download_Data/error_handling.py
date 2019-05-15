"""
Program Title:
    error_handling.py
    
Author: 
    Mike Brice
    
Last Modified:
    Sat Sep 4, 2018

Description: 
    Handles the common errors of the program and sends them to be logged by
    the save_Error.py function.
    
    Handles when the SDSS_Data_URL.txt cant be opened or written to.
    Handles when the .FITs files wont open
    Handles when the SDSS Server cant be reached
    Handles when the program can't delete the .FITs file
    
    Error Level 3 is a critical shutdown error that needs to attempt to 
    resolve the error within 7 attempts spaning ~30 minutes.
    
    Error Level 2 is a critical shutdown error that needs to attempt to 
    resolve the error within 3 attempts spaning ~1 minute.
    
    Error Level 1 is a non critical error that needs to attempt to
    resolve the error within 3 attempts spaning ~1 minute. The program does
    not shutdown with an Error Level 1.
    
"""

# =============================================================================
# Imports
# =============================================================================
import time
import sys
import thread

from save_Error import save_Error as save_Error

# =============================================================================
# error_Handling | Handles the IOErrors for the program       
# =============================================================================
'''
Function Parameters
    text - first text statement to be printed
    text2 - second text statement
    URL - current URL that the program is working with
    level - is either 1,2,3 representing the level of error
    fun - function
    *args - arguments for fun

Function Returns
    ret - the return value of fun
'''
def error_handling(text, text2, URL, level, fun, *args):
    
    wait = [5,10,30,60,300,600,900] # Seconds to wait for next attempt
    attempts = 0 # Initialize the attempts counter
    status = True # Sets the loop terminator to True
    
    # Exit the loop if there are no errors or that the error has been resolved.
    # Loop until either the error has been resolved or until the desired number
    # of attempts have been performed and then perform safe shutdown.
    while status:
        try:
            ret = fun(*args) # Tries to run the function
            status = False # If the function is successful terminate the loop
            
        except IOError as ioe:
            
            print ("IOError: Attempting to %s again in %d seconds" % (text, wait[attempts]))
            time.sleep(wait[attempts])
            
            # Error Level 3 = Critical Error associated with internet connection | ~30 minutes of attempts before shutdown
            if level == 3:
                # If there have been 7 attempts then shutdown the program
                if attempts == 6:
                    save_Error(level, "Failed to %s" % (text2), URL, str(ioe)) # Log the error
                    print ("\nError Level 3\nCritical Error:\nFailed to %s\nCheck error log for information\n" % (text2))
                    thread.interrupt_main() # Flag the KeyboardInterrupt in the main thread to perform safe shutdown
                    sys.exit() # Kill the thread
            
            # Error Level 2 = Crtical Error associated with saving and loading the .csv and .txt files | ~1 minute of attempts before shutdown
            elif level == 2:
                # If there have been 3 attempts then shutdown the program
                if attempts == 2:
                    save_Error(level, "Failed to %s" % (text2), URL, str(ioe)) # Log the error
                    print ("\nError Level 2\nCritical Error:\nFailed to %s\nCheck error log for information\n" % (text2))
                    thread.interrupt_main() # Flag the KeyboardInterrupt in the main thread to perform safe shutdown
                    sys.exit() # Kill the thread
                
            # Error Level 1 = Non-Critical Error associated with .FITs file reading | ~1 minute of attempts before skipping to next file
            else:
                # If there have been 3 attempts then skip this file and move on.
                if attempts == 2:
                    save_Error(level, "Failed to %s" % (text2), URL, str(ioe)) # Log the error
                    print ("\nError Level 1\nFailed to %s\nCheck error log for information\n" % (text2))
                    sys.exit() # Kill the thread

            attempts += 1 # Increment the attempts
            
        except Exception as we:
            print ("Error: Attempting to %s again in %d seconds" % (text, wait[attempts]))
            time.sleep(wait[attempts])
            
            if attempts == 2:
                save_Error(level, "Failed to %s" % (text2), URL, str(we)) # Log the error
                print ("\nError Level 1\nFailed to %s\nCheck error log for information\n" % (text2))
                sys.exit() # Kill the thread
            
            attempts += 1 # Increment the attempts
            
    # If attempts > 0 and the thread has not been killed display that the error has been resolved
    if attempts > 0:
        print ("Error has been resolved")
        
    return ret