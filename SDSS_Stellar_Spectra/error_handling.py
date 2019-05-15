'''
Program Title: 
    error_handling.py

Author:
    Michael J. Brice
    
Last Modified:
    Fri Sep 14, 2018
    
Description:
    Handles the errors of the package
    
'''

import time
from traceback import print_exc

# Under development


#==============================================================================
# retrieve_error | Still developing
#==============================================================================
def retrieve_error(message = ""):

    print_exc()
    time.sleep(.5)
    print "%s\n" % message
    
#==============================================================================
# download_error | Still developing
#==============================================================================
def download_error():
    print ""

#==============================================================================
# critical_error | Still developing
#==============================================================================    
def critical_error():
    print ""
    
#==============================================================================
# generic_error | Still developing
#==============================================================================
def generic_error():
    
    print_exc()
    time.sleep(.5)
    print ""
    
    