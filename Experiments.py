#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 17:07:40 2019

@author: Michael J. Brice
"""

import numpy as np
from math import log10
import time
from tqdm import tqdm
import multiprocessing
from functools import partial

# =============================================================================
# feature_selection
# =============================================================================
def feature_selection(flux, wave, a, nThreads = 64):
    """
    Feature Selection
    
    flux -- numpy.ndarray of shape(# samples, # measurements) of flux
    wave -- numpy.ndarray of shape(# samples, # measurements) of wave
    a    -- wavelength of absorption line
    nThreads -- number of threads for parallelization (default = 64)
    
    return -- reduced flux and wave array
    """
    
    print("Absorption Line: %s" % a) 
    time.sleep(1) # Sleep the main thread to allow the text to print

    # Number of measurements around the absorption line
    bounds = 8
    
    # New Flux and Wavelength array
    flux1 = np.zeros((len(flux), bounds*2 + 1))
    wave1 = np.zeros((len(flux), bounds*2 + 1))
        
    # Thread pool
    pool = multiprocessing.Pool(nThreads)
        
    res = [] # Results array
    
    # create a function for parallization
    func2 = partial(feature_selection_worker, a2 = a) 
    
    # Loops through all the threads
    for i in tqdm(pool.imap(func2, zip(flux, wave)), total=len(flux), unit = "Samples"):
        res.append(i)
    
    # Finalize thread pool
    pool.close()
    pool.join()
    
    # Copy data to the new flux and wavelength arrays
    for i in range(0,len(flux)):
        flux1[i] = res[i][0]
        wave1[i] = res[i][1]

    return flux1, wave1

# =============================================================================
# find_nearest
# =============================================================================
def find_nearest(array, value):
    """
    Find Nearest
    
    array -- the array to search
    value -- the value to find the nearest
    
    return -- index and element of nearest value 
    """
    
    array = np.asarray(array) # Force array to be a numpy array
    idx = (np.abs(array - value)).argmin() # Find the closest array element to value
    return idx, array[idx]
 
# =============================================================================
# feature_selection_worker
# =============================================================================
def feature_selection_worker(it, a2):

    """
    Feature Selection Worker
    
    it -- Zip of flux and wavelength numpy.ndarrays
    a2 -- absorption line for feature selection
    
    return -- reduced flux and wavelength array for a specific sample
    """
    
    # Extracts flux and wavelength from it
    flux = it[0]
    wave = it[1]
    
    # Number of measurements around the absorption line
    bounds = 8

    # Gets the index of the absorption line found within this sample
    index, value = find_nearest(wave, log10(a2))
    flux = flux[index-bounds:index+bounds+1] # extracts the flux values around the absorption line
    wave = wave[index-bounds:index+bounds+1] # extracts the wavelength values around the absorption line
    
    return flux, wave


# =============================================================================
# Main 
# =============================================================================
  
# U = Undersampled, H = Hybrid, 0 = Oversampled
# U - 2530, Default - 453378, H - 957398, O - 2657466
samples = 2657466 # Number of Samples
folder = "./Balanced/" # Folder location of data
balance_type = "O" # File extension of Balance type of the data
fs = "Oversampled" # Full name of balance type used for storing data

# Load the data from the Numpy memmap objects
flux = np.memmap(folder + "SDSS_Flux_R_%s.dat" % (balance_type), dtype = np.float, mode='r', shape = (samples,4617))
cls = np.memmap(folder + "SDSS_Class_R_%s.dat" % (balance_type), dtype = "S5", mode='r', shape = (samples))
wave = np.memmap(folder + "SDSS_Wave_R_%s.dat" % (balance_type), dtype = np.float, mode='r', shape = (samples,4617))    
  

print("Classifying Experiment")

start = time.clock() # Start time for feature selection
flux1, wave1 = feature_selection(flux, wave, 4102.89) # Reduce flux and wavelength arrays around absorption line one

flux2, wave2 = feature_selection(flux, wave, 4227.79) # Reduce flux and wavelength arrays around absorption line two

# Combine the two reduced flux and wavelength arrays
flux = np.append(flux1, flux2, axis=1)
wave = np.append(wave1, wave2, axis=1)
tmK = time.clock() - start # stop time for feature selecton

# Loads in the stellar classes that are present in data
f = open("Distribution.txt", "r")
classes = []
for line in f:
    classes.append(line.rstrip()) 
    
y = []
# Convert classes to strings
for j, sample in enumerate(cls):
    y.append(sample.decode('UTF-8'))

y = np.asarray(y).reshape(-1) # Reshape array

print("10 Fold CV")

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_validate
from sklearn.ensemble import RandomForestClassifier

cv = 10 # 10 Fold Cross Validation
    
k = [3, 5, 7, 10, 15, 20] # K number of neighbors
classifier = "KNN"
print("Experiment %s %s" % (classifier, fs))

# Loop through KNN experiments
for i in tqdm(range(0,6), total=6, unit = "Experiments"):
    clf = KNeighborsClassifier(n_neighbors=k[i]) # KNN classifier
    
    # Gets the results from the CV experiments
    scores = cross_validate(clf, flux, y, cv = cv, scoring = ('accuracy', 'precision_macro', 'recall_macro', 'f1_macro'), return_train_score = False)
    
    # Store the data into a file each loop... Minimizes data loss if unexpected 
    f = open("Experiment_%s_%s.txt" % (classifier, fs),"a+")
    f.write("K = %s, CV = %s, Accuracy = %s, Accuracy_std = %s, Precision = %s, Precision_std = %s, Recall = %s, Recall_std = %s, F1 = %s, F1_std = %s\n" 
            % (k[i], cv, scores['test_accuracy'].mean() * 100, scores['test_accuracy'].std(), scores['test_precision_macro'].mean(), 
               scores['test_precision_macro'].std(), scores['test_recall_macro'].mean(), scores['test_recall_macro'].std(), 
               scores['test_f1_macro'].mean(), scores['test_f1_macro'].std()))
    
    f.close() # Close file
    
    # Store time data for each experiment
    f = open("Experiment_%s_%s_time.txt" % (classifier, fs),"a+")
    f.write("K = %s, Feature Select = %s seconds, Train = %s seconds, Test = %s seconds\n" % (k[i], tmK, scores['fit_time'].mean(), scores['score_time'].mean()))
    f.close()
    
classifier = "RF"
print("Experiment %s %s" % (classifier, fs))

k = [10,50,100,150,200,250] # Number of trees in Random Forest

# Loop through Random Forest experiments
for i in tqdm(range(0,6), total=6, unit = "Experiments"):
    clf = RandomForestClassifier(n_estimators = k[i]) # Random Forest classifier
    scores = cross_validate(clf, flux, y, cv = cv, scoring = ('accuracy', 'precision_macro', 'recall_macro', 'f1_macro'), return_train_score = False)
    
    f = open("Experiment_%s_%s.txt" % (classifier, fs),"a+")
    f.write("K = %s, CV = %s, Accuracy = %s, Accuracy_std = %s, Precision = %s, Precision_std = %s, Recall = %s, Recall_std = %s, F1 = %s, F1_std = %s\n" 
            % (k[i], cv, scores['test_accuracy'].mean() * 100, scores['test_accuracy'].std(), scores['test_precision_macro'].mean(), 
               scores['test_precision_macro'].std(), scores['test_recall_macro'].mean(), scores['test_recall_macro'].std(), 
               scores['test_f1_macro'].mean(), scores['test_f1_macro'].std()))
    f.close()
    
    f = open("Experiment_%s_%s_time.txt" % (classifier, fs),"a+")
    f.write("K = %s, Feature Select = %s seconds, Train = %s seconds, Test = %s seconds\n" % (k[i], tmK, scores['fit_time'].mean(), scores['score_time'].mean()))
    f.close()

