"""
Program Title:
    get_Data.py
    
Author: 
    Mike Brice
    
Last Modified:
    Tue Sep 11, 2018

Description: 
    Gets the flux, wavelength, emission and absorption lines and the class
    from the .FITs file.
    
    When accessing data, the error handler function is called where the 
    function table.read and arguments are passed as arguments. This is done to 
    ensure that any possible error that occurs when accessing the data is 
    handled.
"""

# =============================================================================
# Imports
# =============================================================================
from numpy import array as array
from astropy.table import Table as table
from error_handling import error_handling as error_handling

# =============================================================================
# get_Data | Accesses and Returns the data in the .FITs files
# =============================================================================
'''
Function Parameters
    fileName - Name of the file to the .FITs file
    current_URL - URL of current file | Used only for the error log if an unsolvable error occures
    
Function Returns
    wavelentgh - Float array of wavelength data in logoritmic form
    model - Array of flux data | Calibrated Flux from SDSS Pipeline
    cls - Class of the star
    lines - Emission and Absorption lines
'''
def get_Data(fileName, current_URL):
    
    # Gets all the data out of the fits file
    data = error_handling("read data header from .FITS file", "read data header from .FITS file", 
                          "\nError Level 1\nURL at failure: %s" % (current_URL), 
                          1, table.read, fileName, 1) # Loads the table at Header 1
    info = error_handling("read information header from .FITS file", "read information header from .FITS file", 
                          "\nError Level 1\nURL at failure: %s" % (current_URL), 
                          1, table.read, fileName, 2) # Loads the table at Header 2
    ea_lines = error_handling("read emission and absorption lines header from .FITS file", 
                              "read emission and absorption lines header from .FITS file", 
                              "\nError Level 1\nURL at failure: %s" % (current_URL), 
                              1, table.read, fileName, 3) # Loads the table at Header 3
    
    wavelength = array(data['loglam']) # Gets the wavelengths from Header 1
    model = array(data['model']) # Gets the flux intensities from Header 1
    cls = info['SUBCLASS'][0] # Gets the classification from Header 2
    Z = info['Z'][0] # Gets the redshift from Header 2
    Z_ERR = info['Z_ERR'][0] # Gets the redshift error from Header 2
    lines = array(ea_lines['LINEWAVE']) # Gets the emission and absorption lines from Header 3
    
    return wavelength, model, cls, lines, Z, Z_ERR