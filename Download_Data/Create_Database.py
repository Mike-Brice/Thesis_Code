import sqlite3

# Creates Databases
connection = sqlite3.connect("SDSS_DR14_BOSS_Redshift.db")

cursor = connection.cursor()

cursor.execute("CREATE TABLE Accepted (Key INTEGER PRIMARY Key, URL VARCHAR, File_Name VARCHAR, Class CHAR(2), Flux VARCHAR, Wavelength VARCHAR, EALines VARCHAR, Z FLOAT, Z_ERR FLOAT, Date DATE);")
cursor.execute("CREATE TABLE Rejected (Key INTEGER PRIMARY Key, URL VARCHAR, File_Name VARCHAR, Class CHAR(2), Reason VARCHAR, Date DATE);")
connection.close()