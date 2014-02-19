import os
import struct
import numpy as np
import operator

values = {}  # We will store all the data in the dictionary "values"
fp = open("Setup1.awg","rb")

# Read first 200 parameters from file
for i in range(200):
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
typeNames = []

NameFlag = 0
DataFlag = 0
TimestampFlag = 0
for x in range(len(output_list)):
    byte_num = output_list[x][1][1]
    value_num = output_list[x][1][2]

    # remove numbers from name
    s = output_list[x][0]
    name_string = ''.join([i for i in s if not i.isdigit()])
    print('%s\t%s' % (s,name_string))

    if name_string not in typeNames:
        typeNames.append(name_string)
        if byte_num == 2:
             output.append([name_string,'int16',value_num])
        elif byte_num == 4:
            output.append([name_string,'int32',value_num])
        elif byte_num== 8:
            output.append([name_string,'float64',value_num])
        else:
##            name_string = output_list[x][0]
            if "NAME" in name_string:
                output.append([name_string,'WFM_name',value_num])
            elif "DATA" in name_string:
                output.append([name_string,'WFM_data',value_num])
            elif "TIMESTAMP"in name_string:
                output.append([name_string,'16byteTimeStamp',value_num])
##     output.append([output_list[x][0], output_list[x][1][2], output_list[x][1][1]]) #Only print attribute name and value, not the byte sizes and indices we stored for later use
##print output


seq_name = 'AWGFileFormat_Dictionary.txt';
fseq = open(seq_name,'w')

for x in range(0,len(output)):
    fseq.write('%s\t%s\t%s\t\n' %(output[x][0],output[x][1],output[x][2]))
fseq.close()