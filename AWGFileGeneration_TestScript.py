import os
import struct
import numpy as np
import operator
import sys

AWG_Dict = {}  # We will store all the data in the dictionary "values"
AWG_byte = {}  # We will store all the data in the dictionary "bytes"

seq_dir = 'C:\Users\Felix\Documents\GitHub\AWG_Generation_Scripts'
os.chdir(seq_dir)

##seq_name = '';
fdict = open("AWGFileFormat_Dictionary.txt","rb")

name_byte = 22



# Read first 200 parameters from file
for i in range(0,200):
    try:
        line = fdict.readline()
        name_string = line.split('\t')[0]
        byte_string = line.split('\t')[1]
        byte_num = line.split('\t')[2]
##        AWG_Dict[name_string] = [i,name_string,byte_string]
##        data[1].append('hello')
        print name_string
        AWG_Dict[name_string] = byte_string
        AWG_byte[name_string] = byte_num
        # Add to values dictionary, each entry containing the index (order in which read from file), byte length of data as stored on AWG, and value data itself
##        values[name_string] = [i,value_bytes,value]
    except:
        break # Don't die on exception e.g. corrupt file or EOF, just break out of for loop

fdict.close() # Close file

DesiredValues = [('MAGIC',5000),
                 ('VERSION',1),
                 ('SAMPLING_RATE',1000000000.0),
                 ('CLOCK_SOURCE',0),
                 ('TRIGGER_SOURCE',0),
                 ('JUMP_TIMING',0),
                 ('RUN_MODE',0),
                 ('MARKER2_LOW_1',0),
                 ('MARKER2_HIGH_1',1),
                 ('OUTPUT_WAVEFORM_NAME_1','CWESR_python0c1'),
                 ('OUTPUT_WAVEFORM_NAME_2','CWESR_python0c2'),
                 ('OUTPUT_WAVEFORM_NAME_3','CWESR_python0c3'),
                 ('OUTPUT_WAVEFORM_NAME_4','CWESR_python0c4')]

CLOCK_SOURCE = 0 # 0: internal, 1: external
TRIGGER_SOURCE = 0 # 0: internal, 1: external
JUMP_TIMING = 0 # 0: Sync, 1: ASync
RUN_MODE = 0 # 0: Continuous, 1: Triggered, 2: Gated, 3: Sequence



base_filename = 'CWESR_python'

base_dir = 'F:\AWG'
os.chdir('F:\AWG')
basefile_dir = ('%s\\%s' %(base_dir,base_filename))
if not os.path.exists(basefile_dir):
    os.makedirs(base_filename)
    print ('Making subdirectory: %s' % base_filename)

awg_name = os.path.join(basefile_dir,('AWGFILE_%s.awg' %(base_filename)))
fawg = open(awg_name,'w')





print ('\n------------')
print('SAVING AWG FILES')
for x in range (0,len(DesiredValues)):
    paramName = DesiredValues[x][0] # get parameter name

    # remove numbers from name
    s = paramName
    paramTypeLookup = ''.join([i for i in s if not i.isdigit()])

    paramDataType = AWG_Dict[paramTypeLookup] # lookup typecast for value
##    paramByteNum = AWG_byte[paramTypeLookup] # lookup byte num for value
    paramValue = DesiredValues[x][1] # read desired value
    paramTypeCast = ('np.%s(%s)' % (paramDataType,paramValue))
    name_byte = len(paramName.encode('UTF-8'))+1

    if paramDataType == 'int16': # populates of the value is a SHORT
        fawg.write(struct.pack('<L',len(paramName.encode('UTF-8'))+1))
        fawg.write(struct.pack('<L',2))
        fawg.write('%s\x00' % (paramName))
        print ('%s %s %s' % (len(paramName.encode('UTF-8'))+1,paramName,eval(paramTypeCast)))
        fawg.write(struct.pack('<h',eval(paramTypeCast)))

    if paramDataType == 'int32': # populates of the value is a FLOAT
        fawg.write(struct.pack('<L',len(paramName.encode('UTF-8'))+1))
        fawg.write(struct.pack('<L',4))
        fawg.write('%s\x00' % (paramName))
        print ('%s %s' % (paramName,eval(paramTypeCast)))
        fawg.write(struct.pack('<f',eval(paramTypeCast)))

    if paramDataType == 'float64': # populates of the value is a LONG
        fawg.write(struct.pack('<L',len(paramName.encode('UTF-8'))+1))
        fawg.write(struct.pack('<L',8))
        fawg.write('%s\x00' % (paramName))
        print ('%s %s' % (paramName,eval(paramTypeCast)))
        fawg.write(struct.pack('<d',eval(paramTypeCast)))

    if paramDataType == 'WFM_name':
        print ('%s %s' % (paramName,paramValue))
        fawg.write(struct.pack('<L',len(paramName.encode('UTF-8'))+1))
        fawg.write(struct.pack('<L',len(paramValue.encode('UTF-8'))+1))
        fawg.write('%s\x00' % (paramName))
        fawg.write('%s\x00' % paramValue)

    if paramDataType == 'WFM_data':
        print ('%s' % (paramName))
        fawg.write(struct.pack('<L',len(paramName.encode('UTF-8'))+1))
        fawg.write(struct.pack('<L',sys.getsizeof(paramValue)))
        fawg.write('%s\x00' % (paramName))
        fawg.write('%s\x00' % paramValue)

    if paramDataType == '16byteTimeStamp':
        print ('%s' % (paramName))
        fawg.write(struct.pack('<L',len(paramName.encode('UTF-8'))+1))
        fawg.write(struct.pack('<L',16))
        fawg.write('%s\x00' % (paramName))
        fawg.write('%s\x00' % paramValue)
##    fawg.write('\n')
fawg.close()