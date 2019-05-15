"""
Program Title:
    Weka_ARFF.py
    
Author:
    Mike Brice
    
Last Modified:
    Mon Sep 24, 2018
    
Description:
    Takes data that is inserted and creates an ARFF file for Weka to use.
    
"""

# =============================================================================
# create_arff
# =============================================================================
'''
Function Parameters:
    file_name - the name of the arff file, excluding the file extension
    
Function Returns:
    returns 1 if succesfull and -1 if not succesful
'''
def create_arff(file_name, numberAttributes, data):
    
    if len(data[0]) != 2:
        print "Please insert a list of lists with only the class and flux data"
        
        return -1
    else:
        global fileName
        fileName = file_name
        
        # If the file exists, if not return -1
        try:
            
            __initialize_arff(numberAttributes)
            __insert_data_arff(numberAttributes, data)
            
        except IOError as e:
            
            print str(e)
            
            return -1
            
        print "ARFF Complete"
        
        return 1

# =============================================================================
# append_arff        
# =============================================================================
'''
Function Parameters:
    file_name - the name of the arff file
    data - the dataset to be inserted
    
Function Returns:
    returns 1 if succesfull and -1 if not succesful
'''
def append_arff(file_name, data):
    
    if len(data[0]) != 2:
        print "Please insert a list of lists with only the class and flux data"
        
        return -1
    else:
        global fileName
        fileName = file_name
        
        # If the file exists, if not return -1
        try:
            __insert_data_arff(__get_number_attributes(), data)
            
        except IOError as e:
            
            print str(e)
            
            return -1
        
        print "ARFF Insert Complete"
        
        return 1
    
# =============================================================================
# __get_number_Attributes    
# =============================================================================
'''
Function Parameters:
    None
    
Function Returns:
    returns the number of attributes in the file
'''
def __get_number_attributes():
    f = open('%s.arff' % fileName, 'r')
    text = f.read()
    f.close()
    return text.count("@ATTRIBUTE") - 1
    
# =============================================================================
# __initialize_arff
# =============================================================================
'''
Function Parameters:
    numberAttributes - the number of attributes to be put into the file
    
Function Returns:
    None
'''
def __initialize_arff(numberAttributes):
    cls = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
        
    # Creates the arff file
    f = open('%s.arff' % fileName, 'w')
    
    # Add in the relation line
    f.write('@RELATION %s\n' % fileName)
    
    # Insert the number of attributes into the file
    for i in range(1, numberAttributes+1):
        f.write('@ATTRIBUTE flux%d NUMERIC\n' % (i))
        
    # Inserts the class attribute
    f.write('@ATTRIBUTE class {')
    
    # Loop through the 7 classes
    for i in range(0, 7):
        # Loop through the first 9 subclasses followed by a comma: 0-8
        for j in range(0,9):
            f.write('%s%d,' % (cls[i],j))
        
        # If it is not the last class add in the subclass 9 followed by a comma
        if i != 6:
            f.write('%s9,' % (cls[i]))
    
    # The last class is inserted with out a comma        
    f.write('M9}\n\n@Data\n')
        
    f.close()
        
# =============================================================================
# __insert_data_arff
# =============================================================================
'''
Function Parameters:
    numberAttributes - the number of attributes to be put into the file
    data - the dataset to be inserted

Function Returns:
    None
'''
def __insert_data_arff(numberAttributes, data):
    
    # Opens the arff file
    f = open('%s.arff' % fileName, 'a')
    
    # If the first column in the first row is a string, then index1 is the
    # second column and index2 is the first column
    if data[0][0].isalpha():
        index1 = 0
        index2 = 1
        
    # Else index1 is the first column and index2 is the second column
    else:
        index1 = 1
        index2 = 0
    
    # Insert each row into the arff
    for row in data:
        __insert(numberAttributes, row[index1], row[index2], f)
        
    f.close
    
# =============================================================================
# __insert
# =============================================================================
'''
Function Parameters:
    numberAttributes - the number of attributes to be put into the file
    flux - the flux array to be inserted into the arff file
    cls - the cls for the current stellar spectra
    f - file
    
Function Returns:
    None
'''
def __insert(numberAttributes, flux, cls, f):
    
    # Loop through the number of attributes
    for i in range(0, numberAttributes):
        
        # If i is less than the number of flux then insert the flux
        if i < len(flux):
            f.write('%f, ' % flux[i])
            
        # If i is larger than the length of flux fill in with a ?
        else:
            f.write('?, ')
            
    # writes in the class at the end of the data
    f.write('%s\n\n' % cls)
    