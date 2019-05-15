#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 22:30:58 2018

@author: mike
"""

import sqlite3
from urls import load_URLs, save_URLs


connection = sqlite3.connect("SDSS_DR14_Redshift.db") # Connects to the database
                
cursor = connection.cursor() # Makes a cursor to go throug the database
           
# Gets all of the columns from the table at the particular Column and Identifier
cursor.execute("SELECT * FROM Accepted WHERE Key = (SELECT MAX(Key) FROM Accepted)") 
ret = cursor.fetchone() 
print ret[0]
        
connection.close() # Close the database connection     
    
connection = sqlite3.connect("SDSS_DR14_Redshift.db") # Connects to the database
                
cursor = connection.cursor() # Makes a cursor to go throug the database
           
# Gets all of the columns from the table at the particular Column and Identifier
cursor.execute("SELECT * FROM Rejected WHERE Key = (SELECT MAX(Key) FROM Rejected)") 
ret2 = cursor.fetchone() 
print ret2[0]
        
connection.close() # Close the database connection


list_URLs = load_URLs()

index = list_URLs.index(str(ret[1]))

index2 = list_URLs.index(str(ret2[1]))

if index > index2:
    list_URLs = list_URLs[index+1:]
    
else:
    list_URLs = list_URLs[index2+1:]

save_URLs(list_URLs)
