#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 22:01:18 2018

@author: mike
"""

import numpy as np
import random as random
from SDSS_Stellar_Spectra.retrieve_data import retrieve_one
from SDSS_Stellar_Spectra.process_data import redshift as red


# Number of samples
number_samples = 453378

# Loop terminator
balanced = False

sample_size = 55 # Undersampled = 55 | Hybrid = 20813 | Oversampled = 57771

# Class labels

f = open("Distribution.txt", "r")
classes = []
for line in f:
    classes.append(line)
    
#classes = ["B9", "B6", "A0", "F9", "F5", "F2", "G2", "G0", "K7", "K5", "K3", "K1", "M9", "M8", "M7", "M6", "M5", "M4", "M3", "M2", "M1", "M0"]
samples = [0] * len(classes)
expected = sample_size * len(classes)

folder = "./SDSS_Stellar_Spectra/"
#remove_samples = [244232, 356065] # The two G5 classes that are being discarded
remove_samples = []

# Sets if its the redshifted spectra
redshift = "_R"
balance_type = "U"

number_features = 4617
# Opens the DAT files for reading and writing
flux = np.memmap(folder + "SDSS_Flux%s.dat" % redshift, dtype = np.float, mode = "r+", shape = (number_samples, number_features))
cls = np.memmap(folder + "SDSS_Class%s.dat" % redshift, dtype = 'S5', mode = "r+", shape = (number_samples))
wave = np.memmap(folder + "SDSS_Wave%s.dat" % redshift, dtype = np.float, mode = "r+", shape = (number_samples, number_features))
redshift_arr = np.memmap(folder + "SDSS_Redshift%s.dat" % redshift, dtype = np.float, mode = "r+", shape = (number_samples))

# Initializes the array for storing each class's indexes
sample_index = [None] * len(classes)

# Initializes the arrays for each class
for i in range(0, len(classes)):
    sample_index[i] = []

# Loops though the different classes
for i, clss in enumerate(classes):
    
    clss = clss.rstrip()
    # Loops through the classes in the DAT file
    for j, sample in enumerate(cls):
        sample = sample.decode('UTF-8')
            
        # If the sample is the current class
        if sample == clss:
            samples[i] += 1 # Increase the count for that class by one
            sample_index[i].append(j) # Add the current classes index to the array


if balance_type == "H":
    print ("Balancing: Hybrid")

elif balance_type == "U":
    print ("Balancing: Undersampled")

elif balance_type =="O":
    print ("Balancing: Oversampled")
    
else:
    print ("Feature Select")
          
print ("Initial Number of Samples: %s" % (sum(samples)))

# Loops 0 to the total number of classes
for i in range(0,len(classes)):
    #random_samples = random.sample(xrange(0, samples[i]), samples[i] - 572)
    
    if samples[i] >= sample_size:
        p = np.linspace(0, samples[i], num = samples[i], dtype = np.int, endpoint=False)
        random_samples = random.sample(list(p), sample_size) # Determines the random indexes of the samples of the current class to be kept
        
        temp_array = np.take(sample_index[i], random_samples) # Copies the classes indexes for the current class into a temporary array
        
        number_samples -= samples[i] - sample_size # Decreases the number of samples by the amount being removed
        
        # Copy the the random indexes of the current class to be kept
        for j in temp_array:
            remove_samples.append(j)
            
    else:
        
        current_size = 0
        
        while sample_size > current_size:
            
            if (current_size + len(sample_index[i])) <= sample_size:
                
                for j in sample_index[i]:
                    remove_samples.append(j)
                
                current_size += len(sample_index[i])
                
            else:
                size = sample_size - current_size
   
                p = np.linspace(0, samples[i], num = samples[i], dtype = np.int, endpoint=False)
                random_samples = random.sample(list(p), size) # Determines the random indexes of the samples of the current class to be kept
        
                temp_array = np.take(sample_index[i], random_samples) # Copies the classes indexes for the current class into a temporary array
                
                # Copy the the random indexes of the current class to be kept
                for j in temp_array:
                    remove_samples.append(j)
                    
                current_size += size
                
        number_samples += current_size - samples[i]
                
#number_samples -= 2 # Remove two for the G5 class

print ("Deleting Samples")    
#remove_samples = np.unique(remove_samples) # Ensures that the random indexes are unique

# Changes the destination folder 
folder = "./Balanced/"

new_flux = np.memmap(folder + "SDSS_Flux%s_%s.dat" % (redshift, balance_type), dtype = np.float, mode = "w+", shape = (number_samples, number_features))
new_cls = np.memmap(folder + "SDSS_Class%s_%s.dat" % (redshift, balance_type), dtype = 'S5', mode = "w+", shape = (number_samples,))
new_wave = np.memmap(folder + "SDSS_Wave%s_%s.dat" % (redshift, balance_type), dtype = np.float, mode = "w+", shape = (number_samples, number_features))
        
del new_cls
del new_flux
del new_wave
# Copies the samples that are being kept to the new DAT files
# Index = index in memmap
from tqdm import tqdm
with tqdm(total=len(remove_samples), unit="Samples") as pbar:
    for i, index in enumerate(remove_samples):
                
        # Makes new copies of the DAT files
        new_flux = np.memmap(folder + "SDSS_Flux%s_%s.dat" % (redshift, balance_type), dtype = np.float, mode = "r+", shape = (number_samples, number_features))
        new_cls = np.memmap(folder + "SDSS_Class%s_%s.dat" % (redshift, balance_type), dtype = 'S5', mode = "r+", shape = (number_samples,))
        new_wave = np.memmap(folder + "SDSS_Wave%s_%s.dat" % (redshift, balance_type), dtype = np.float, mode = "r+", shape = (number_samples, number_features))
        Z = redshift_arr[index] # Gets the Redshift for this sample
        
        temp = np.random.uniform(0,0.0008) # Generates a random new redshift for this sample
        monte = np.random.uniform(0,1) # Generates a random variable 
        
        # If greater than 0.5 make temp negative, else positive
        if monte > 0.5:
            temp = -1 * temp
        
        # Finds the relative redshift value for the transformation
        Z = temp - Z
        
        new_cls[i] = cls[index]
        new_flux[i] = flux[index]
        new_wave[i] = red(wave[index], Z)
        
        # Finalizes and Closes the new DAT files
        del new_cls
        del new_flux
        del new_wave
        pbar.update(1) 
        
    # Closes the original DAT files
    del cls
    del flux
    del wave

    new_cls = np.memmap(folder + "SDSS_Class%s_%s.dat" % (redshift, balance_type), dtype = 'S5', mode = "r", shape = (number_samples,))
    print ("Expected Final Number of Samples: %s" % expected)
    print ("Actual Final Number of Samples: %s" % number_samples )
    print ("Final Shape of Class Array: %s" % new_cls.shape[0])
    del new_cls
    

'''
# Displays the new count for each class
folder = "./Balanced/"

f = open("Distribution.txt", "r")
classes = []
for line in f:
    classes.append(line)
redshift = "_R"
balance_type = "H"
number_samples = 957398
new_cls = np.memmap(folder + "SDSS_Class%s_%s.dat" % (redshift, balance_type), dtype = 'S5', mode = "r", shape = (number_samples))


new_samples = [0] * len(classes)
for i, clss in enumerate(classes):
    clss = clss.rstrip()
    for j, sample in enumerate(new_cls):
        sample = sample.decode('UTF-8')
        if sample == clss:
            new_samples[i] += 1
         

'''       
            
    
    