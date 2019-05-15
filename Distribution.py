#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 19:07:25 2019

@author: Michael J. Brice
"""

import numpy as np
from matplotlib import pyplot as plt

# Class of stellar spectra
major = ["O", "B", "A", "F", "G", "K", "M"]
minor = [9,8,7,6,5,4,3,2,1,0]
mk = ["I", "II", "III", "IV", "V", "VI"]

classes = []
    
for ma in major:
    for mi in minor:
        for m in mk:
            classes.append((ma+str(mi)+m))
                
                
redshift = "_R" # Redshifted or rest spectra data file extension
balance_type = "" # Balance type spectra data file extension

# Load class data from spectra data
cls = np.memmap("./SDSS_Stellar_Spectra/SDSS_Class%s%s.dat" % (redshift, balance_type), mode = "r", dtype = "S5")

# Count samples
new_samples = np.zeros((420,))
for i, clss in enumerate(classes):
    for j, sample in enumerate(cls):
        sample = sample.decode('UTF-8')
        if sample == clss:
            new_samples[i] += 1
            
indices = np.where(new_samples != 0)[0] # find indices where the count is not 0

samples = new_samples[indices] # copy all non zero indices

classes = np.asarray(classes)
classes = classes[indices] # copy all non zero indices class labels

# Add an addition element representing all 0 sample size classes
samples = np.append(samples, 0)
classes = np.append(classes, "RC")

y_pos = np.arange(len(classes))

# Plot the data
plt.rcParams.update({'font.size': 16})

fig, ax = plt.subplots(figsize=(20, 10))

ax.bar(y_pos, samples, align='center', alpha=1, color = "black")


ax.set_xticks(y_pos)
ax.set_xticklabels(classes)

plt.xticks(rotation=90)
plt.xlabel('Stellar Classes', fontsize=25)
plt.ylabel('Number of Instances of each Class', fontsize=25)
plt.title('Distribution of Stellar Classes in Database: Total Instances = %d' % sum(samples), fontsize=25)

plt.grid(linewidth=2) 
plt.savefig("Distribution.png") # Saves plot in working directory

