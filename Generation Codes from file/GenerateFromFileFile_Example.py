import os
import struct
import numpy as np
import operator

# Set directory
awg_dir = 'C:\Users\Admin\Documents\GitHub\AWG_Generation_Scripts\Generation Codes from file'
os.chdir(awg_dir)
import TekAWG # import AWG functions

# Set save directory
filename = 'AWG_FullFormat_PLE.txt'
SaveFileName = 'PLE_python'
SaveFilePath = 'M:\Shared Projects\Cold Diamond\AWG'

# Open AWG full file
fawg = fdict = open(filename,"rb")

##WFM_length = 1000 # ns

# Read Channel Array Information
ChanName = {}
FullChanString = [];

print ('***************************')
print ('READING CHANNEL INFORMATION')

for i in range(0,12):
    line = fawg.readline()
    FullChanString.append([])
    if line != '\r\n':
            name = line.split(' = ')[0]
            name = name.rstrip('\n')
            stringval = line.split(' = ')[1]
            stringval = stringval.rstrip(']\r\n')
            stringval = stringval.lstrip('[')
            ChanStringArr = stringval.split(',')
            NumElements = len(ChanStringArr)/2

            FullChanString[i].append(name)
            print ('%s:' % name)
            for j in range(0,NumElements):
                timeArray = ChanStringArr[2*j].strip("()''")
                valArray = ChanStringArr[2*j+1].strip("()''")

                # Replace stripped closing parentheses to numpy call in string to eval
                # Only works for numpy commands with only ONE parameter such as numpy.arange(10)
                if timeArray.find('numpy') != -1:
                    timeArray += ')'
                    #print "DEBUG" + timeArray + "DEBUG"
                if valArray.find('numpy') != -1:
                    valArray += ')'
                    #print "DEBUG" + valArray + "DEBUG"

                FullChanString[i].append([timeArray,valArray])
                print ('\t(%s,%s)' % (timeArray,valArray))

# Read VARIABLES
Continue = 1
FullVariableString = []

print ('*****************')
print ('READING VARIABLES')

while Continue == 1:
    line = fawg.readline()
##    print line
    if '[' in line:
        stringval = line.split('[')[1]
        if ']' in line:
            Continue = 0
            stringval = stringval.strip(']')
##        print stringval

    elif ']' in line:
        Continue = 0
        stringval = line.strip(']')
    else:
        stringval = line

    stringval = stringval.strip("'\r\n'")

    if stringval != '':
        Expression = stringval.strip("()[]'',")
        print Expression
        FullVariableString.append(Expression)

# Read AWG VALUES
FullDesValsString = (())
Continue = 1

print ('******************')
print ('READING AWG VALUES')

while Continue == 1:
    line = fawg.readline()
##    print line
    if '[' in line:
        stringval = line.split('[')[1]
        if ']' in line:
            Continue = 0
            stringval = stringval.strip(']')

    elif ']' in line:
        Continue = 0
        stringval = line.strip(']')
    else:
        stringval = line

    stringval = stringval.strip("'\r\n'")

    if stringval != '':
        ParamName = stringval.split(',')[0].strip("()''")
        ParamVal = stringval.split(',')[1].strip("()''")
        print ('%s -> %s' % (ParamName,ParamVal))
        FullDesValsString = FullDesValsString + (tuple((ParamName,ParamVal)),)

fawg.close()

AWG_Dict = TekAWG.Load_AWGDictFile()


# Generate and Populate Channel Information
(FullChanArray,NumWFMs,WFM_length) = TekAWG.Create_Chan_Array(FullChanString,FullVariableString)
# Save Sequence and Waveform Files
(WFMnames,WFMStrings) = TekAWG.Save_Sequence_File(FullChanArray,NumWFMs,WFM_length,SaveFileName,SaveFilePath)

print FullDesValsString
# Save AWG file with desired values
TekAWG.Save_AWG_File(FullDesValsString,AWG_Dict,FullChanArray,NumWFMs,WFM_length,SaveFileName,SaveFilePath)



# This is the code to populate the waveform in the AWG File
# DOES NOT WORK YET (leave commented out)

##NumChans = 4

##for i in range(0,NumChans):
##    ParamName = ('OUTPUT_WAVEFORM_NAME_%d' % i)
##    ParamVal = WFMnames[i][0]
##    print ('%s -> %s' % (ParamName,ParamVal))
##
##    FullDesValsString = FullDesValsString + (tuple((ParamName,ParamVal)),)
##
##offset = 26


##for j in range(0,NumWFMs):
##    for i in range(0,NumChans):
##        ParamName = ('WAVEFORM_NAME_%d' % (offset+j*NumChans+i))
##        ParamVal = WFMnames[j*NumChans+i][0]
##        print ('%s -> %s' % (ParamName,ParamVal))
##        FullDesValsString = FullDesValsString + (tuple((ParamName,ParamVal)),)
##
##        ParamName = ('WAVEFORM_TYPE_%d' % (offset+j*NumChans+i))
##        ParamVal = 2
##        print ('%s -> %s' % (ParamName,ParamVal))
##        FullDesValsString = FullDesValsString + (tuple((ParamName,ParamVal)),)
##
##        ParamName = ('WAVEFORM_LENGTH_%d' % (offset+j*NumChans+i))
##        ParamVal = WFM_length
##        print ('%s -> %s' % (ParamName,ParamVal))
##        FullDesValsString = FullDesValsString + (tuple((ParamName,ParamVal)),)
##
##        ParamName = ('WAVEFORM_DATA_%d' % (offset+j*NumChans+i))
##        ParamVal = WFMStrings[j*NumChans+i][0:5*WFM_length]
##        FullDesValsString = FullDesValsString + (tuple((ParamName,ParamVal)),)

print FullDesValsString

TekAWG.Save_AWG_File(FullDesValsString,AWG_Dict,FullChanArray,NumWFMs,WFM_length,SaveFileName,SaveFilePath)



