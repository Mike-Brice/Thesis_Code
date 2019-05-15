"""
Program Title:
    urls.py
    
Author: 
    Mike Brice
    
Last Modified:
    Sat Sep 4, 2018

Description:
    load_URLs loads the remaining URLs from the SDSS_Data_URLs.txt file into a
    list / queue and returns it for the program to use.
    
    save_URLs saves the remaining URLs into the SDSS_Data_URLs.txt when the 
    program shutsdown.
    
    Everytime a new thread is created, a URL is popped from the list / queue.
"""

# =============================================================================
# load_URLs | Loads the list of URLs from the URL text file 
# =============================================================================
'''
Function Returns
    list_URLs - list of all remaining URLs for SDSS data downloads
'''
def load_URLs():
    
    list_URLs = [] # Initialize the URL list
    
    # Open the URL file
    with open("SDSS_Data_URL.txt", 'rb') as f:
        
        # Add URLs to the URL list
        for line in f:
            list_URLs.append(line)
    
    return list_URLs

# =============================================================================
# save_URLs | Saves the list of URLs from the URL list
# =============================================================================
'''
Function Parameters
    list_URLs - list of all remaining URLs for SDSS data downloads
'''
def save_URLs(list_URLs):
    
    with open("SDSS_Data_URL.txt", 'w') as f:
        for URL in list_URLs:
            f.write(URL)