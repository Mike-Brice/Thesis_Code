'''
Program Title: 
    impute.py

Author:
    Mike Brice
    
Last Modified:
    Fri Sep 14, 2018
    
Description:
    Compares the last K flux values and performs a strategy to fill in missing 
    data in the flux array.
    
'''

# =============================================================================
# Imports
# =============================================================================
import numpy as np

# =============================================================================
# FluxImputer
# =============================================================================
'''
Class Description:
    Used to shape and if applicable replace missing values in the Flux.
    
    A utility function for shapping and replacing missing values for 
    wavelengths for plotting purposes is included.
'''
class FluxImputer():
    
    # =========================================================================
    # __init__
    # =========================================================================
    '''
    Constructor Parameters:
        fill_value - what to initially fill in missing values with
        number_Features - the total number of features
        strategy - the strategy to be used to fill in the missing values
    '''
    def __init__(self, number_Features, strategy):
        
        # Set the fill_value for missing values to be np.nan
        self.fill_value = np.nan
        
        # Set the number features to the user provided number
        self.number_Features = number_Features
        
        # Set the strategy used to fill in missing features
        self.strategy = strategy
        
        # Initialize the length of the original array
        self.length_X = 0
        
    # =========================================================================
    # set_sample_feature_length  
    # =========================================================================
    '''
    Function Parameters:
        X - array of flux values (or wavelengths), if the length is less than 
            the desired M features then the missing data is filled with 
            fill_value. If the length is more than the desired M features then 
            the excess with be removed.
        
    Function Returns:
        new_X - array of flux values of the desired M features with missing 
                values replaced.
    '''
    def __fit_to_template(self, X, Y):
                
        from SDSS_Stellar_Spectra.utilities import isclose
        
        template = np.memmap("./SDSS_Stellar_Spectra/SDSS_Template.dat", dtype = np.float, mode = 'r', shape = (1, self.number_Features))
        
        # Finds the first index in Y where it equals the first value in template
        #i, = np.where(Y == template[0][0])
        i = -1
        
        for k, y in enumerate(Y):
            if isclose(y, template[0][0], rel_tol = 0.00001, abs_tol=0.0):
                i = k
                break
        
        # If the first index in Y where it equals the first value in template exists
        if i > -1:

            Y = Y[i:] # Cut everything off of the left to make index 0 of the template and Y equal
            X = X[i:] # Cut everything off of the left to make index 0 of the X correspond to the index of 0 in Y
            
        # If template starts to the left of index 0 in Y then find the first
        # instance of index 0 of Y in template then shift Y to that index
        else:
            
            #j, = np.where(template[0] == Y[0])[0]
            j = -1
            
            for k, t in enumerate(template[0]):
                if isclose(Y[0], t, rel_tol = 0.00001, abs_tol=0.0):
                    j = k
                    break

            new_Y = [self.fill_value] * self.number_Features # Initialize a temp array

            new_Y[j:] = Y[:] # In the new array insert Y[0] starting at index j 
            new_Y[:j] = np.copy(template[0][:j]) # Fill in the missing values with the values from 0 to i in template
            
            Y = new_Y # Copy the temp into Y
            
            #Y = Y[0]
            
            new_X = [self.fill_value] * self.number_Features # Initialize a temp array
            
            new_X[j:] = X[:] # In the new array insert X[0] starting at index i
            X = np.array(new_X) # Copy the temp into X
    
        # Cut off or fill in the ends if needed
        # If the length of X and Y are longer then the number of Features cut off
        # the end features
        if len(Y) > self.number_Features:
            Y = Y[:self.number_Features]

        # Else fill in the missing end features with the fill value
        elif len(Y) < self.number_Features:
            Y = np.append(Y, template[0][len(Y):self.number_Features])
            
        if len(X) > self.number_Features:
            X = X[:self.number_Features]
            
        elif len(X) < self.number_Features:
            missing = [self.fill_value] * (self.number_Features - len(X))
            X = np.append(X, missing)
        
        del template
        
        return X, Y
    
    # =========================================================================
    # fill
    # =========================================================================
    '''
    Function Parameters:
        X - array of shape [N samples, M Features]
        
    Function Returns:
        new_X - array of shape [N samples, M features] with missing values 
                replaced based on the strategy
    '''
    def fill(self, X, Y, K):
        
        X, Y = self.__fit_to_template(X, Y)
        # If the last element in the array X is np.nan then fill in the
        # missing values, if not 
        
        i, = np.where(np.isnan(X))
        
        if len(i) > 0:
            if self.strategy == "Moving Average":
                X = self.__moving_average(X, i,  K)
                X = np.array(X).astype(np.float)
        
        return np.array(X), np.array(Y)

    # =========================================================================
    # __moving_average            
    # =========================================================================
    '''
    Function Parameters:
        array - array of flux values to replace missing values
        n - length of subset to perform the moving average
    
    Function Returns:
        array - array of flux values with missing values replaced with moving
                averages
    '''
    def __moving_average(self, X, i, n=50) :
        
        # Initialize the k list
        k = [] 
        
        # Finds the index when the current element of i does not equal
        # the previous element of i + 1 
        for j, a in enumerate(i):
            
            # If j does not equal 0
            if j != 0:
                
                # Check if the current value and the previous value plus 1 are equal
                if a == i[j-1] + 1:
                    pass # Do nothing
                    
                # If the current value and the previous value plus 1 do not 
                # equal then add the index to k
                else:
                    k.append(j)
                    break
        
        # If the first value in i is 0 then insert the missing values at the
        # beginning of the spectra

        if i[0] == 0:
            
            # If there is no values to insert at the end of the spectra
            k_stat = True
            if len(k) == 0:
                k.append(i[len(i)-1])
                k_stat = False
             
            # Loop over the beginning missing values
            for l in range(k[0], -1, -1):
                sm = 0 # Initialize the sum

                # Sum the next N values
                for j in range(0, n):
                    
                    # Sum the values over the last n values of the array
                    sm += X[(l + 1 + j)]
                
                X[l] = sm / n # Average

            if len(k) != 0 and k_stat:
                # Loop over the end missing values
                for l in range(i[k[0]], i[len(i)-1]+1):
                    sm = 0 # Initialize the sum
                    
                    # Sum the last N values
                    for j in range(0,n):
                        
                        # Sum the values over the last n values of the array
                        sm += X[(l - 1 - j)]
                    
                    X[l] = sm / n # Average
            
        # If the first value is not equal to zero then add the missing values 
        # the end of the spectra
        if i[0] != 0:
                  
            # Loop over all the mising values
            for i in i:
                sm = 0

                # Sum the last N values
                for j in range(0,n):
                    
                    # Sum the values over the last n values of the array
                    sm += X[(i - 1 - j)]

                X[i] = sm / n # Average
                
        #print X
        return X
        
    # =========================================================================
    # extend_wavelengths           
    # =========================================================================
    '''
    Function Parameters:
        X - wavelengths to be extended to the number of features
        
    Function Returns: 
        X - wavelengths at the correct length
        
    Function Description:
        This function is a utility function for modifying wavelengths for
        plotting flux that has had missing values replaced
    '''
    def extend_wavelengths(self, X):
        
        # If the last value in the array is np.nan then insert values into the
        # array
        if np.isnan(X[-1]):
            
            # The difference between the number of features and the length of the
            # original array
            difference = self.number_Features - self.length_X
            
            # Iterating over the difference between the original array and the 
            # number of features
            for j in range(0,difference):
                
                # Insert into the current missing value index the previous
                # wavelength value + 1
                X[j+self.length_X] = X[j + self.length_X - 1] + 1
                
            return X
        
        # If the last element is not np.nan, return the array because there are
        # no missing values
        else:
            return X