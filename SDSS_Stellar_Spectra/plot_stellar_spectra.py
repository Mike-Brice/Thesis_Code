'''
Program Title: 
    plot_stellar_spectra.py

Author:
    Mike Brice
    
Last Modified:
    Fri Sep 14, 2018
    
Description:
    Either plots a single spectra to a file or plots multiple spectra to a 
    single plot and saves to a single file.
    
'''
#==============================================================================
# Imports
#==============================================================================
from matplotlib import pyplot as plt

# =============================================================================
# spectra_plot
# =============================================================================
'''
Function Parameters
    plotName - name of the plot including file type. for example .png
    wave - wavelenghts points (x axis)
    flux - flux points (y axis)
    cls - class of stellar spectra
    fileName - fileName of the stellar spectra .FITS file
    lines - Emission and Absorption lines, default to empty
'''
def spectra_plot(plotName, wave, flux, cls, fileName, lines = []):

    plt.ioff()
    plt.rcParams.update({'font.size': 18})
    plt.figure(num=None, figsize=(12, 6), dpi=80, facecolor='w', edgecolor='k') # Sets size of plot
    plt.plot(wave, flux) # Plots
    #plt.xlim(xmin = wave[0] - 50) # Sets the lower x bound to 50 less than the smallest wavelength
    plt.rcParams.update({'font.size': 22})
    plt.xlabel('Wavelength [$\AA$]') # X axis label
    plt.ylabel('Flux [$10^{-17}$ ergs / s / $cm^2$ / $\AA$]') # Y axis label
    
    # Adds the emission and absorption lines to the plot
    for line in lines:
        plt.axvline(x = line, color = 'tab:gray') # Adds a vertical line representing where the Emission and Absorption lines are
        
    plt.grid() # Adds a grid
    
    # Creates the tile with proper grammer
    if cls[0] == 'A' or cls[0] == 'O':
        plt.title('Spectra of an %s Star: %s' %(cls, fileName))
    else:
        plt.title('Spectra of a %s Star: %s' %(cls, fileName))
    plt.savefig(plotName) # Saves plot in working directory
    
    print ("Plotted and Saved: %s" % (plotName) )

#==============================================================================
# multilayered_spectra_plot  
#==============================================================================
'''
Function Parameters
    plotName - name of the plot including file type. for example .png
    wave - array of different wavelenghts points (x axis)
    flux - array of different flux points (y axis)
    cls - array of different  class of stellar spectra
'''
def multilayered_spectra_plot(plotName, wavelength, flux, cls):
    

    
    plt.ioff()
    
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(wavelength[1], flux[1], "--", linewidth=1, label = "Redshifted Spectra:\nZ = 0.000661", color="red")
    ax.plot(wavelength[0], flux[0], linewidth = 0.5,label = "Rest Spectra", color="black")

    
    #plt.figure(num=None, figsize=(25, 8), dpi=80, facecolor='w', edgecolor='k')
    
    plt.rcParams.update({'font.size': 16})
    plt.xlim(xmin = wavelength[0][0] - 200) # Sets the lower x bound to 50 less than the smallest wavelength
    plt.xlabel('Wavelength [$\AA$]') # X axis label
    plt.ylabel('Flux [$10^{-17}$ ergs / s / $cm^2$ / $\AA$]') # Y axis label

        
    plt.grid() # Adds a grid
    plt.legend(loc = "lower left") # Adds legend to upper right corner of the plot
    
    #plt.title('Multilayered Spectra Plot') # Adds plot title
    
    plt.title('Redshifted vs Rest wavelength Typical A0 Stellar Spectrum ') # Adds plot title

    from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
    axins = zoomed_inset_axes(ax, 40, loc=5) # zoom-factor: 2.5, location: upper-left
    
    axins.plot(wavelength[0], flux[0], color="black")
    axins.plot(wavelength[1], flux[1], "--", linewidth=1.5,  color="red")
    
    #x1, x2, y1, y2 = 3.68, 3.695, 0.7, 0.82 # specify the limits
    x1, x2, y1, y2 = 4700, 4750, 0.81, 0.835 # specify the limits
    axins.set_xlim(x1, x2) # apply the x-limits
    axins.set_ylim(y1, y2) # apply the y-limits
    
    plt.yticks(visible=False)
    plt.xticks(visible=False)
    
    plt.grid() # Adds a grid
    
    
    from mpl_toolkits.axes_grid1.inset_locator import mark_inset
    mark_inset(ax, axins, loc1=2, loc2=4, fc="black", ec="0")
    
    
    '''
    # Plots the wavelengths and flux and label of multiple spectra
    for i in range(0, len(wavelength)):
        
        plt.plot(wavelength[i], flux[i], label = 'Spectra of a %s Star' %(cls[i]))
    '''
    #plt.xlim(xmin = wavelength[0][0] - 50) # Sets the lower x bound to 50 less than the smallest wavelength
    


    plt.savefig(plotName) # Saves plot in working directory
    
    print ("Plotted and Saved: %s" % (plotName) )
    