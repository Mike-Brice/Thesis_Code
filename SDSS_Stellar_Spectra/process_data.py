'''
Program Title: 
    process_data.py

Author:
    Mike Brice
    
Last Modified:
    Fri Sep 14, 2018
    
Description:
    The wavelengths in the .FITS files are defaulted to a logarithmic scale, 
    when the data is returned from the database it needs to be converted to
    base 10.
    
    Flux needs to be scaled to 0 to 1 for Classification.
    
    Processes the data. Since the data is returned from the database as unicode
    strings then the data has to be converted back into its origial types.
    For example flux needs to be converted back into a numpy float array.
    
    If the data is returned from the database on the server then the data is
    returned as a single string, for all data. The string_list_list converts
    the string into a list of lists and then the __process_data_r and
    __process_one_r process the data.
    == This feature is under developement ==
    
'''

#==============================================================================
# Imports
#==============================================================================
import numpy as np

from math import log10
from numpy import amin
from numpy import amax
from numpy import empty
from numpy import array
#from error_handling import generic_error


#==============================================================================
# wavelengths10
#==============================================================================
'''
Function Parameters
    wavelengths - wavelength values to be converted to base 10 from logarithmic
    
Function Returns
    wavelengths - wavelength values in base 10
'''
def wavelengths10(wavelengths):
    
    from SDSS_Stellar_Spectra.utilities import normal_round 
    
    wavelength = [normal_round(10**w) for w in wavelengths] # converts to base 10 from logarithmic
    
    wavelength = array(wavelength)
    
    return wavelength

#==============================================================================
# flux_scaled
#==============================================================================
'''
Function Parameters
    flux - flux points to be scaled to 0 to 1

Function Returns
    scaledflux - flux points on a scale of 0 to 1
'''
def flux_scaled(flux):
    minD = amin(flux) # Min flux value
    maxD = amax(flux) # Max flux value
    
    scaledflux = empty([flux.size, 1]) # Makes an empty array
    
    # Scales the flux values and stores them in scaledflux
    scaledflux = [(fz - minD) / (maxD - minD) for fz in flux]
    
    return scaledflux


# =============================================================================
# Redshift
# =============================================================================
    
def redshift(wavelength_red, Z):
    
    from SDSS_Stellar_Spectra.utilities import normal_round  
           
    wavelength_rest = [None] * len(wavelength_red)
    #wavelength_redshift = [log10(10**w * (Z + 1)) for w in wavelength_rest]  
    
    #wavelength_red[0] = normal_round(log10(10**wavelength_rest[0] * (Z + 1)))
    wavelength_rest[0] = normal_round(log10(10**wavelength_red[0] / (Z+1)))
    #
    for i in range(1, len(wavelength_red)):
        wavelength_rest[i] = wavelength_rest[i-1] + 0.0001
        
    #wavelength_redshift = [log10(10**w * (Z + 1)) for w in wavelength_rest]  
    
    wavelength_rest = np.array(wavelength_rest)
    
    return wavelength_rest
    
    
#==============================================================================
# __process_one
#==============================================================================
'''
Function Parameters:
    data - a tuple that was accessed from the database
    
Function Returns:
    data - a list that has been processed into their appropriate types
'''
def __process_one(data):
    try:
    
        data = list(data)
                
        # Exctract the columns from data and the index of the column
        for i, column in enumerate(data):
      
                # If the column is an int then do not check the other instances
                if isinstance(column, int):
                    pass
                
                # If the column is a float then do not check the other instances
                elif isinstance(column, float):
                    pass
                    
                # If the first character in the column is a letter then convert the column from unicode to string
                elif str(column[0]).isalpha(): 
                    data[i] = str(column)
                  
                # If the first character of the column is [ then convert the column from unicode to a numpy float array
                elif str(column[0] == '['):     
                    column = str(column).split(',') # Splits the column into a list
                    column[0] = column[0].replace("[", "") # Removes the [ from the first number
                    column[len(column)-1] = column[len(column)-1].replace("]", "") # Removes the ] from the last number
                    column = array(column).astype(np.float) # Converts the list into a float array
                    data[i] = column
                    
        return data
    except Exception:
        pass
        #generic_error()

#==============================================================================
# __process_data
#==============================================================================
'''
Function Parameters:
    data - a list of tuples that was accessed from the database
    
Function Returns:
    data - a list of lists that has been processed into their appropriate types
'''
def __process_data(data):
     
    try:
        
        # Converts data from a list of tuples to a list of lists
        data = [list(row) for row in data]
        
        # Exctract the rows from data and the index of the row
        for i, row in enumerate(data):
            
            # Extract the columns from the row and the index of the column
            for j, column in enumerate(row):
                
                # If the column is an int then do not check the other instances
                if isinstance(column, int):
                    pass
                
                # If the column is a float then do not check the other instances
                elif isinstance(column, float):
                    pass
                    
                # If the first character in the column is a letter then convert the column from unicode to string
                elif str(column[0]).isalpha(): 
                    data[i][j] = str(column)
                  
                # If the first character of the column is [ then convert the column from unicode to a numpy float array
                elif column[0] == '[':   
                    
                    column = column.split(',') # Splits the column into a list
                    column[0] = column[0].replace("[", "") # Removes the [ from the first number
                    column[len(column)-1] = column[len(column)-1].replace("]", "") # Removes the ] from the last number
                    column = array(column).astype(np.float) # Converts the list into a float array
                    data[i][j] = column
                    
        return data
    except Exception:
        pass
        #generic_error()
        
#==============================================================================
# __process_one_r | For the client server feature, still developing
#==============================================================================
'''
Function Parameters:
    data - a tuple that was accessed from the database
    
Function Returns:
    data - a list that has been processed into their appropriate types
'''
def __process_one_r(data):
    try:
    
        data = list(data)
                
        # Exctract the columns from data and the index of the column
        for i, column in enumerate(data):
      
                # If the column is an int then do not check the other instances
                if isinstance(column, int):
                    pass
                    
                # If the first character in the column is a letter then convert the column from unicode to string
                elif str(column[0]).isalpha(): 
                    data[i] = str(column)
                  
                # If the first character of the column is [ then convert the column from unicode to a numpy float array
                elif str(column[0] == '['):     
                    column = column.split(' ') # Splits the column into a list
                    column = column[:-1]
                    column[0] = column[0].replace("[", "") # Removes the [ from the first number
                    column[len(column)-1] = column[len(column)-1].replace("]", "") # Removes the ] from the last number
                    column = array(column).astype(np.float) # Converts the list into a float array
                    data[i] = column
                    
        return data
    except Exception:
        pass
        #generic_error()

#==============================================================================
# __process_data_r | For the client server feature, still developing
#==============================================================================
'''
Function Parameters:
    data - a list of tuples that was accessed from the database
    
Function Returns:
    data - a list of lists that has been processed into their appropriate types
'''
def __process_data_r(data):
     
    try:
        
        # Exctract the rows from data and the index of the row
        for i, row in enumerate(data):
            
            # Extract the columns from the row and the index of the column
            for j, column in enumerate(row):
                
                # If the column is an int then do not check the other instances
                if isinstance(column, int):
                    pass
                    
                # If the first character in the column is a letter then convert the column from unicode to string
                elif str(column[0]).isalpha(): 
                    pass
                  
                # If the first character of the column is [ then convert the column from unicode to a numpy float array
                elif column[0] == '[':   
                    
                    column = column.split(' ') # Splits the column into a list
                    column = column[:-1]
                    column[0] = column[0].replace("[", "") # Removes the [ from the first number
                    column[len(column)-1] = column[len(column)-1].replace("]", "") # Removes the ] from the last number
                    column = array(column).astype(np.float) # Converts the list into a float array
                    data[i][j] = column
                    
        return data
    except Exception:
        pass
        #generic_error()        
        
#==============================================================================
# __string_list_list | For the client server feature, still developing
#==============================================================================
def __string_list_list(data, num_columns):
    data = data.split('u')

    data = data[1:]

    for i in range(0, len(data)):
        data[i] = data[i].replace("'", "")
        data[i] = data[i].replace(",", "")
        data[i] = data[i].replace("(", "")
        data[i] = data[i].replace(")", "")
        
    
    data[len(data)-1] = data[len(data)-1].replace("]", "")
    
    data = [data[i:i+num_columns] for i in range(0, len(data), num_columns)]
    
    return data
