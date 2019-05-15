'''
Program Title: 
    utilities.py

Author:
    Mike Brice
    
Last Modified:
    Thu Sep 27, 2018
    
Description:
    All the utility functions for SDSS_Stellar_Spectra package are found here 
    
'''

# =============================================================================
# Imports
# =============================================================================
import numpy as np
import os
import math

from SDSS_Stellar_Spectra.retrieve_data import retrieve_set
from SDSS_Stellar_Spectra.impute import FluxImputer
from SDSS_Stellar_Spectra.process_data import flux_scaled, redshift

from tqdm import tqdm
from math import ceil


class memoryMap():
    
    # number_Samples can be a list, same with database
    def __init__(self, number_Samples, number_Features, flux_file, class_file, wave_file, redshift_file, redshifted, database, length_Class = 5, override = True):
               
        # Set initial values
        if len(number_Samples) == 1:
            self.number_Samples = number_Samples[0]
            self.number_Samples_Arr = [number_Samples]
            self.database = [database]
            
            # Finds the closest smaller number to the number of samples that is divisiable by 500
            # and finds the extra. This is used for the memmap creator function.
            
            # Find the quotient 
            q = int(number_Samples[0] / 500) 
            
            divisiable = [None] * 1
            # 1st possible closest number 
            divisiable = 500 * q  
            
            extra = [None] * 1
            extra = number_Samples[0] - divisiable
            
        else:
            self.number_Samples = number_Samples[0]
            self.number_Samples_Arr = number_Samples
            self.database = database
            
            divisiable = []
            extra = []
            
            for sample in number_Samples:
                # Find the quotient 
                q = int(sample / 500) 
                
                # 1st possible closest number 
                divisiable.append(500 * q)
                
                extra.append((sample - (500 * q)))
          
        # initializes fields
        self.number_Features = number_Features
        self.divisiable = divisiable
        self.extra = extra
        self.redshifted = redshifted
        self.extend = 0

        self.override = override
        self.length_Class = "S%s" % (length_Class)
        self.flux_file = "./SDSS_Stellar_Spectra/" + flux_file
        self.class_file = "./SDSS_Stellar_Spectra/" + class_file
        self.wave_file = "./SDSS_Stellar_Spectra/" + wave_file
        self.redshift_file = "./SDSS_Stellar_Spectra/" + redshift_file
        
    def create_map(self, columns = "*"):
        
        # Memap and flux imputer for redshifted data
        if self.redshifted:
            # Key, URL, File_Name, Class, Flux, Wavelength, EALines, Date
            index = [3,4,5,7] # Class, Flux, Wavelength, redshift
            
            # if the column database identifier is not * (all) then identify the order that the user entered in the column ID
            if columns != "*":
                for i, column in enumerate(columns.split(", ")):
                    
                    if column == "Flux":
                        index[1] = i
    
                    if column == "Wavelength":
                        index[2] = i
    
                    if column == "Class":
                        index[0] = i
                        
                    if column == "Z":
                        index[3] = i
                        
            print ("Creating Numpy MemMap with data from %s" % (self.database))
        
            amount = 500
            
            # If overriding is enabled, override the data files
            if self.override:
                flux = np.memmap(self.flux_file, dtype = np.float, mode='w+', shape=(sum(self.number_Samples_Arr), self.number_Features))
                del flux
            
                cls = np.memmap(self.class_file, dtype = self.length_Class, mode='w+', shape=(sum(self.number_Samples_Arr),1))
                del cls
                
                wave = np.memmap(self.wave_file, dtype = np.float, mode='w+', shape=(sum(self.number_Samples_Arr), self.number_Features))
                del wave
                
                Z = np.memmap(self.redshift_file, dtype = np.float, mode='w+', shape=(sum(self.number_Samples_Arr), 1))
                del Z
            
            # Loop through all database queries to build the data files
            with tqdm(total=int(sum(self.divisiable) / amount) + 3 , unit="500 Specta") as pbar:
                
                # Loop if there is more than one database being used to create the data files
                for j in range(0, len(self.number_Samples_Arr)):
                    offset = 0
                    if j != 0:
                        self.number_Samples += self.number_Samples_Arr[j]
                        self.extend += self.number_Samples_Arr[j-1]
                                   
                    while True:
                        
                        # Retrieves data from the SQL database
                        sub_data = retrieve_set("Accepted", amount, offset, columns, self.database[j], False)
                                
                        # If all data has been retrieved stop
                        if sub_data == None:
                            print ("Done")
                            break
                        
                        else:
                            
                            flux_imputer = FluxImputer(number_Features = self.number_Features, strategy = "Moving Average") # Creates Imputer object
                            
                            # Open Data files
                            flux = np.memmap(self.flux_file, dtype = np.float, mode = 'r+', shape = (self.number_Samples + self.extend, self.number_Features))
                            cls = np.memmap(self.class_file, dtype = self.length_Class, mode='r+', shape=(self.number_Samples + self.extend,))
                            wave = np.memmap(self.wave_file, dtype = np.float, mode = 'r+', shape = (self.number_Samples + self.extend, self.number_Features))
                            Z = np.memmap(self.redshift_file, dtype = np.float, mode = 'r+', shape = (self.number_Samples + self.extend,))
                              
                            # If the retrieved data is less than the amount requested load and break the loop because all data has been retrieved
                            if offset == self.divisiable[j]: 
                                for i, row in enumerate(sub_data):      
                                    
                                    if i == self.extra[j]:
                                        break
                                    
                                    row[index[1]] = flux_scaled(row[index[1]]) # Scale Flux
                                            
                                    row[index[1]], row[index[2]] = flux_imputer.fill(row[index[1]], row[index[2]], 50) # Fill in missing values
                                    
                                    cls[self.extend+offset+i] = row[index[0]] # Store class
                                    Z[self.extend+offset+i] = row[index[3]] # Store redshift value
                                    
                                    row[index[1]] = row[index[1]].reshape(self.number_Features,) # Reshape Flux array
                                    row[index[2]] = row[index[2]].reshape(self.number_Features,) # Reshape Wavelengths array
                                    
                                    flux[self.extend+offset+i][:] = row[index[1]][:] # Store Flux array
                                    wave[self.extend+offset+i][:] = row[index[2]][:] # Store Wavelengths array
                            
                            else:
                                for i, row in enumerate(sub_data):
        
                                    row[index[1]] = flux_scaled(row[index[1]]) # Scale Flux

                                    row[index[1]], row[index[2]] = flux_imputer.fill(row[index[1]], row[index[2]], 50)
                                    
                                    cls[self.extend+offset+i] = row[index[0]]
                                    Z[self.extend+offset+i] = row[index[3]]

                                    
                                    row[index[1]] = row[index[1]].reshape(self.number_Features,) # Flux
                                    row[index[2]] = row[index[2]].reshape(self.number_Features,) # Wavelengths
                                    
                                    flux[self.extend+offset+i][:] = row[index[1]][:]
                                    wave[self.extend+offset+i][:] = row[index[2]][:]
                    
                            offset += amount
                          
                            pbar.update(1)  
                            
                            del flux
                            
                            del cls
                            
                            del wave
                
            return 1
        
# =============================================================================
        # Memmap and flux imputer for rest data
        else:
            # Key, URL, File_Name, Class, Flux, Wavelength, EALines, Date
            index = [3,4,5,7] # Class, Flux, Wavelength, redshift
            
            if columns != "*":
                for i, column in enumerate(columns.split(", ")):
                    
                    if column == "Flux":
                        index[1] = i
    
                    if column == "Wavelength":
                        index[2] = i
    
                    if column == "Class":
                        index[0] = i
                        
                    if column == "Z":
                        index[3] = i
    
                                                
            print ("Creating Numpy MemMap with data from database")
        
            amount = 500

            if self.override:
                flux = np.memmap(self.flux_file, dtype = np.float, mode='w+', shape=(sum(self.number_Samples_Arr), self.number_Features))
                del flux
            
                cls = np.memmap(self.class_file, dtype = self.length_Class, mode='w+', shape=(sum(self.number_Samples_Arr),1))
                del cls
                
                wave = np.memmap(self.wave_file, dtype = np.float, mode='w+', shape=(sum(self.number_Samples_Arr), self.number_Features))
                del wave
                        
            with tqdm(total=int(sum(self.divisiable) / amount)+1 , unit="500 Specta") as pbar:
                
                for j in range(0, len(self.number_Samples_Arr)):
                    offset = 0
                    if j != 0:
                        self.number_Samples += self.number_Samples_Arr[j]
                        self.extend += self.number_Samples_Arr[j-1]
                
                    while True:
                        
                        sub_data = retrieve_set("Accepted", amount, offset, columns, self.database[j], False)
                                
                        if sub_data == None:
                            print ("Done")
                            break

                        else:
                            
                            flux_imputer = FluxImputer(number_Features = self.number_Features, strategy = "Moving Average")
                            flux = np.memmap(self.flux_file, dtype = np.float, mode = 'r+', shape = (self.number_Samples + self.extend, self.number_Features))
                            cls = np.memmap(self.class_file, dtype = self.length_Class, mode='r+', shape=(self.number_Samples + self.extend,))
                            wave = np.memmap(self.wave_file, dtype = np.float, mode = 'r+', shape = (self.number_Samples + self.extend, self.number_Features))
                            
                            if offset == self.divisiable[j]: 
                                for i, row in enumerate(sub_data):      
                                    
                                    if i == self.extra[j]:
                                        break
                                    
                                    row[index[1]] = flux_scaled(row[index[1]]) # Scale Flux
                                    row[index[2]] = redshift(row[index[2]], row[index[3]]) # Redshift wavelengths
                                    row[index[1]], row[index[2]] = flux_imputer.fill(row[index[1]], row[index[2]], 50)
                                    cls[self.extend+offset+i] = row[index[0]]
                                    
                                    row[index[1]] = row[index[1]].reshape(self.number_Features,) # Flux
                                    row[index[2]] = row[index[2]].reshape(self.number_Features,) # Wavelengths
                                    
                                    flux[self.extend+offset+i][:] = row[index[1]][:]
                                    wave[self.extend+offset+i][:] = row[index[2]][:]
                            
                            else:
                                for i, row in enumerate(sub_data):
        
                                    row[index[1]] = flux_scaled(row[index[1]]) # Scale Flux
                                    row[index[2]] = redshift(row[index[2]], row[index[3]]) # Redshift wavelengths
                                    
                                    row[index[1]], row[index[2]] = flux_imputer.fill(row[index[1]], row[index[2]], 50)
                                    cls[self.extend+offset+i] = row[index[0]]
                                                                    
                                    row[index[1]] = row[index[1]].reshape(self.number_Features,) # Flux
                                    row[index[2]] = row[index[2]].reshape(self.number_Features,) # Wavelengths
                                    
                                    flux[self.extend+offset+i][:] = row[index[1]][:]
                                    wave[self.extend+offset+i][:] = row[index[2]][:]
                    
                            offset += amount
                          
                            pbar.update(1)  
                            
                            del flux
                            
                            del cls
                            
                            del wave
                        
            return 1
 
# =============================================================================
#   under development     
# =============================================================================
    def open_map(self):
            
        return np.memmap(self.flux_file, dtype = np.float, mode='r', shape = (734342,4617)), np.memmap(self.class_file, dtype = self.length_Class, mode='r', shape = (734342,1))

# =============================================================================
#  under developement
# =============================================================================
    def close_map(self, flux, cls):
        
        del flux
        del cls
        
# =============================================================================
# count_classes
# =============================================================================
'''
Function Parameters:
    cls - list of all the classes
    
Function Returns:
    count - a list of the total counts for each class, in the order of
    O0, O1, O2, O3, ... M7, M8, M9
'''
def count_classes(cls):
    count = [0] * 60
    
    clss = ["B", "A", "F", "G", "K", "M"]
    subclss = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    for c in cls:
        for j, cl in enumerate(clss):
            for subcl in subclss:
                if str(c) == cl+str(subcl):
                    count[j*10+subcl] += 1
                    
    return count

# =============================================================================
# remove_data
# =============================================================================
'''
Function Parameters:
    data - list of lists that has the data for each spectra
    index - the column index of the flux
    lower_limit - the lower limit of the number of flux
    
Function Returns:
    data - list of lists that has the data for each spectra minus those that
           have a flux length less than the lower_limit
'''
def remove_data(data, index, lower_limit):
        
    i = 0
    #with tqdm(total = len(data), unit="Flux") as pbar:            
    for row in data:
        if len(row[index]) <= lower_limit:
            del data[i]
            
        else:
            i += 1
            #pbar.update(1)
    
    return data

# =============================================================================
# argsort
# =============================================================================
'''
Function Parameters:
    scores - array of feature rankings
    sort - sorting algorithm (default = mergesort)
    
Function Returns:
    an array of indices that results in scores being sorted
'''
def argsort(scores, sort = 'mergesort'):
    return np.argsort(scores, kind=sort)

# =============================================================================
# normal_round
# =============================================================================
'''
Python built in round function rounds even numbers at 0.5 up and odd numbers at 0.5 down
Therefore a custom round was needed

Function Parameters:
    n - number to be rounded
    
Function Returns:
    temp - the rounded number
'''
def normal_round(n):
    
    temp = int(n*10000)/float(10000)
    
    if round(n - temp,6) >= 0.00005:
        temp = temp + 0.0001
        return temp
    return temp

# =============================================================================
# isclose
# =============================================================================
'''
Function Parameters:
    a - value 1
    b - value 2
    rel_tol = relative tolerance
    abs_tol = absolute tolerance
    
Function Returns:
    True if the two values are close enough
'''
def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol, abs_tol)
  
# =============================================================================
# classLabelsWorker
# =============================================================================
'''
Worker function for the parallel process of classLabels

Function Parameters:
    txt - current class label

Function Returns:
    returns a numberical value representing the text class
'''
def classLabelsWorker(txt):
    clas = ["O","B","A","F","G","K","M"]
    sub = ["9","8","7","6","5","4","3","2","1","0"]
    mk = ["I", "II", "III", "IV", "V", "VI"]
    number = np.arange(0, 42000, 100)
    for i, cl in enumerate(clas):
        for j in sub:
            for m, m1 in enumerate(mk):
                if cl+j+m1 == txt:
                    return number[i*60 + (9 - int(j)) + ((m) * 10 - 1)]

# =============================================================================
# classLabels                
# =============================================================================
'''
Function Parameters:
    clss - array of class labels
    
Function Returns:
    returns an array of numberical values representing the text class labels
'''
def classLabels(clss):
    
    clss = np.copy(clss)
    
    from multiprocessing import Pool
    
    p = Pool(len(clss))
    clss = p.map(classLabelsWorker, clss)
            
    return np.array(clss).astype(np.int)
        
    