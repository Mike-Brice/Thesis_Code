"""
Program Title:
    SDSS_Data_Download_Main.py
    
Author: 
    Mike Brice
    
Last Modified:
    Sat Sep 4, 2018

Description: 
    Downloads and extracts the useful information from the .FITS files
    of stellar spectra from the Sloan Digitial Sky Survey (SDSS) data run 14 
    from the SDSS Science Archieve Server (SAS) found here:
    https://dr14.sdss.org/optical/spectrum/view?id=81268&plate=685&mjd=52203&fiberid=473
    and inserts them into the SQLite database SDSS_Data.db.
      
    The useful data consists of the Flux, Class, Wavelengths, Emission and 
    Absorption lines, and File Name. Some of the data found at the SAS contains 
    star classifications that are not used in this thesis and therefore are 
    rejected. The file names of the rejected data are included in the Rejected
    Table in the database. All accepted star classes are from O, B, A, F, G, K, 
    and M with subclasses ranging from 0 to 9.

    The data is inserted into this file in the order in which they are 
    downloaded from the SAS. The data is presented at the SAS in order of 
    Modified Julian Date, which is the time and date in which the data was 
    collected. The data represented in this file will not undergo pre 
    processing and will represent the form in which it is presented in the 
    .FITS files from the SAS.
    
    SAS search parameters are RUN2D select all, Spectrograph select SDSS, 
    Class select STAR, leave the rest of the fields blank.

""" 

# =============================================================================
# Imports
# =============================================================================
from tqdm import tqdm

from error_handling import error_handling as error_handling
from workerThread import workerThread as workerThread
from urls import load_URLs as load_URLs
from urls import save_URLs as save_URLs

# =============================================================================
# Start of Program
# =============================================================================
list_URLs = error_handling("open SDSS_Data_URL.txt", "open SDSS_Data_URL.txt", "\nError Level 2", 2, load_URLs)
stored_exception = False

# Loop terminates when either all data has been extracted or KeyboardInterrupt 
# has occured for safe shutdown
with tqdm(total = len(list_URLs), unit = "Spectra") as pbar:
    while len(list_URLs) > 0:
        
        try:
            # If the KeyboardInterrupt occures, kill the loop and perform safe shutdown
            if stored_exception:
                break
            
            worker_Thread = workerThread(list_URLs.pop(0), "SDSS_DR14_BOSS_Redshift.db") # Create a new worker thread with current url and database
            worker_Thread.start() # Start the worker thread
            
            worker_Thread.join() # Wait till the worker thread is finished
        
            del worker_Thread # Delete the worker thread
        
        except KeyboardInterrupt:
            stored_exception = True
            
        pbar.update(1)

# Save the remaining URLs at shutdown. 
error_handling("save URL list", "save URL list", "\nError Level 3", 
                       3, save_URLs, list_URLs) # Save the URL txt file

if stored_exception:
    print "\nSafe Termination Complete"       
    
else:
    print "\nAll relevant data has been inserted into SDSS_Data.csv"
