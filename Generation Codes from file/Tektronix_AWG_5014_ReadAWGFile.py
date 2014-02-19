#-------------------------------------------------------------------------------
# Name:        Tektronix AWG 5014C Read AWG Binary File
# Purpose:     Read .AWG Binary Setup File into Python Dictionary
#
# Author:      Andrew Yeats
#
# Created:     10/12/2013
# Copyright:   (c) Admin 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import struct
import numpy as np
import operator

values = {}  # We will store all the data in the dictionary "values"
fp = open("Setup1.awg","rb")

# Read first 200 parameters from file
for i in range(4):
    try:
        name_bytes, = struct.unpack("<L",fp.read(4))  #Read 32bit little-endian unsigned long repreesenting number of bytes in parameter name
        value_bytes, = struct.unpack("<L",fp.read(4)) # Read 32bit little-endian unsigned long representing number of bytes in parameter data
        name_string = fp.read(name_bytes) #Read parameter name string
        name_string = name_string[:len(name_string)-1] #Clear NULL char from end of string

        #Assign given number of value bytes to corect size variable, else treat as string
        if value_bytes == 2:
            value = np.fromfile(fp,dtype='int16',count=1)[0]
        elif value_bytes == 4:
            value = np.fromfile(fp,dtype='int32',count=1)[0]
        elif value_bytes == 8:
            value = np.fromfile(fp,dtype='float64',count=1)[0]
        else:
            value = fp.read(value_bytes)

        # Add to values dictionary, each entry containing the index (order in which read from file), byte length of data as stored on AWG, and value data itself
        values[name_string] = [i,value_bytes,value]

    except:
        break # Don't die on exception e.g. corrupt file or EOF, just break out of for loop

fp.close() # Close file

# Generate sorted list from dictionary, sorting by index (the order originally read from file)
output_list = sorted(values.iteritems(),key=operator.itemgetter(1))
output = []
for x in range(len(output_list)):
     output.append([output_list[x][0], output_list[x][1][2], output_list[x][1][1]]) #Only print attribute name and value, not the byte sizes and indices we stored for later use
print output

