# Tek AWG program
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import numpy
import re
import sys
import os
import struct

##os.chdir('C:\Users\Felix\Documents\GitHub\AWG_Generation_Scripts')

# Parse channel information

def Parse_Channel(ChanCode,ChanNum,FullVariableString):

    for i in range(0,len(FullVariableString)):
##        print FullVariableString[i]
        exec(FullVariableString[i])

    bufferLength = numpy.zeros(len(ChanCode)+1)
    print ('PARSING CHAN%s, %d element(s)' % (ChanNum,len(ChanCode)))
    NumWFMs = 1
    for idx, element in enumerate(ChanCode):
        el_time = element[0]
        el_val = element[1]

        if el_time.isdigit():
            print('%d : Found constant digit, %d' % (idx,eval(el_time)))
            bufferLength[idx] = eval(el_time)
        else:
            if el_time.find('numpy') != -1:
                elementArr = eval(el_time) # cast array as integers
                bufferLength[idx] = max(elementArr)
                NumWFMs = len(elementArr)
                print('%d : Found numpy equation {%s} buffer length = %d, number of waveforms %d' % (idx,el_time,bufferLength[idx],NumWFMs))

            elif len(re.split('[-+*/]', el_time)) != 1:
                print ('%d : Found string equation, {%s} = %d' % (idx,el_time,eval(el_time)))
                bufferLength[idx] = eval(el_time)
            else:
                print('%d : Found string constant, %s = %d' % (idx,el_time,eval(el_time)))
                bufferLength[idx] = eval(el_time)

    totalBufferLength = sum(bufferLength)
    bufferLength[idx+1] = WFM_length-totalBufferLength
    if bufferLength[idx+1] >= 0:
        print('NO PARSING ERRORS FOUND: Total Buffer Length = %s ns\n' % totalBufferLength)
        return (bufferLength,NumWFMs)
    else:
        print ('ERROR: total buffer length %s exceeds waveform length %s\n' % (totalBufferLength,WFM_length))
        sys.exit(0)


# Populate Channels
def Populate_Channel(ChanCode,ChanNum,FullVariableString,NumWFMs):
    for i in range(0,len(FullVariableString)):
##        print FullVariableString[i]
        exec(FullVariableString[i])

    ChanArrVal = numpy.zeros(shape=(NumWFMs,WFM_length))
    for wfm in range(0,NumWFMs):
        ChanArrIdx = 0 # reset Channel Array Index
        for idx, element in enumerate(ChanCode):
            el_time = element[0]
            el_val = element[1]
            if el_time.find('numpy') != -1:
                elementArr = numpy.int32(eval(el_time))
                bufferLength = max(elementArr)
                for x in range(0,elementArr[wfm]):
                    ChanArrVal[wfm,ChanArrIdx+x] = eval(el_val)
                ChanArrIdx = ChanArrIdx+bufferLength
            else:
                for x in range(0,eval(el_time)):
                    ChanArrVal[wfm,ChanArrIdx] = eval(el_val)
                    ChanArrIdx = ChanArrIdx+1
    print('Populated Chan%s: NO ERRORS' % ChanNum)
    return ChanArrVal

# Populate Channels
def Populate_Marker(MarkerCode,ChanNum,FullVariableString,NumWFMs):
    for i in range(0,len(FullVariableString)):
##        print FullVariableString[i]
        exec(FullVariableString[i])

    MarkerArrVal = numpy.uint8(numpy.zeros(shape=(NumWFMs,WFM_length)))
    for wfm in range(0,NumWFMs):
       MarkerArrIdx = 0 # reset Channel Array Index
       for idx, element in enumerate(MarkerCode):
            el_time = element[0]
            el_val = element[1]
            if el_time.find('numpy') != -1:
                elementArr = numpy.int32(eval(el_time))
                bufferLength = max(elementArr)
                for x in range(0,elementArr[wfm]):
                    if el_val == 'HIGH':
                        MarkerArrVal[wfm,MarkerArrIdx+x] = 1
                    elif el_val == 'LOW':
                        MarkerArrVal[wfm,MarkerArrIdx+x] = 0
                    else:
                        print ('ERROR: unknown marker value')
                MarkerArrIdx = MarkerArrIdx+bufferLength
            else:
                for x in range(0,eval(el_time)):
                    if el_val == 'HIGH':
                        MarkerArrVal[wfm,MarkerArrIdx] = 1
                    elif el_val == 'LOW':
                        MarkerArrVal[wfm,MarkerArrIdx] = 0
                    else:
                        print ('ERROR: unknown marker value')

                    MarkerArrIdx = MarkerArrIdx+1

    print('Populated Chan%s: NO ERRORS' % ChanNum)
    return MarkerArrVal


##AWG_model = '5014'
##
##clock = 1 #ns
##piPulse = 10 #ns


# CONSTANTS


##if AWG_model == '5014':
##    print('Setting up for AWG %s' % AWG_model)
##    numChans = 4
##    numMrksPerChan = 2
##elif AWG_model == '520':
##    print('Setting up for AWG %s' % AWG_model)
##    numChans = 2
##    numMrksPerChan = 2

def Parse_Channel_FullChanString(FullChanString,ChanNum):
    ChanLen = len(FullChanString[ChanNum])
    ChanVal = (())
    if ChanLen > 1:
        ChanName = FullChanString[ChanNum][0]
        for i in range(1,ChanLen):
##            print(FullChanString[ChanNum][i])
            ChanVal = ChanVal + (tuple((FullChanString[ChanNum][i][0],FullChanString[ChanNum][i][1])),)
        print ('%s => %s' % (ChanName,ChanVal))
        return ChanVal
    else:
        print ('INVALID CHAN STRING: Not enough elements in array')

def Create_Chan_Array(FullChanString,FullVariableString):
    print('---------------------------------------------------')
    print('EXECUTING VARIABLE LIST')
    for i in range(0,len(FullVariableString)):
        print FullVariableString[i]
        exec(FullVariableString[i])
    print AOM_DELAY
    print('---------------------------------------------------')
    print('PARSING FULL CHANNEL STRING')

    Chan1Val = Parse_Channel_FullChanString(FullChanString,0)
    Chan1Mark1 = Parse_Channel_FullChanString(FullChanString,1)
    Chan1Mark2 = Parse_Channel_FullChanString(FullChanString,2)

    Chan2Val = Parse_Channel_FullChanString(FullChanString,3)
    Chan2Mark1 = Parse_Channel_FullChanString(FullChanString,4)
    Chan2Mark2 = Parse_Channel_FullChanString(FullChanString,5)

    Chan3Val = Parse_Channel_FullChanString(FullChanString,6)
    Chan3Mark1 = Parse_Channel_FullChanString(FullChanString,7)
    Chan3Mark2 = Parse_Channel_FullChanString(FullChanString,8)

    Chan4Val = Parse_Channel_FullChanString(FullChanString,9)
    Chan4Mark1 = Parse_Channel_FullChanString(FullChanString,10)
    Chan4Mark2 = Parse_Channel_FullChanString(FullChanString,11)
    print ('------------------')
##    print FullChanString

    # Parse channels
    (buffChan1,NumWFMCh1) = Parse_Channel(Chan1Val,'1',FullVariableString)
    (buffCh1M1,NumWFMCh1M1) = Parse_Channel(Chan1Mark1,'1M1',FullVariableString)
    (buffCh1M2,NumWFMCh1M2) = Parse_Channel(Chan1Mark2,'1M2',FullVariableString)
    maxBufLen1 = max([sum(buffChan1),sum(buffCh1M1),sum(buffCh1M2)])

    (buffChan2,NumWFMCh2) = Parse_Channel(Chan2Val,'2',FullVariableString)
    (buffCh2M1,NumWFMCh2M1) = Parse_Channel(Chan2Mark1,'2M1',FullVariableString)
    (buffCh2M2,NumWFMCh2M2) = Parse_Channel(Chan2Mark2,'2M2',FullVariableString)
    maxBufLen2 = max([sum(buffChan2),sum(buffCh2M1),sum(buffCh2M2)])

    (buffChan3,NumWFMCh3) = Parse_Channel(Chan3Val,'3',FullVariableString)
    (buffCh3M1,NumWFMCh3M1) = Parse_Channel(Chan3Mark1,'3M1',FullVariableString)
    (buffCh3M2,NumWFMCh3M2) = Parse_Channel(Chan3Mark2,'3M2',FullVariableString)
    maxBufLen3 = max([sum(buffChan3),sum(buffCh3M1),sum(buffCh3M2)])

    (buffChan4,NumWFMCh4) = Parse_Channel(Chan4Val,'4',FullVariableString)
    (buffCh4M1,NumWFMCh4M1) = Parse_Channel(Chan4Mark1,'4M1',FullVariableString)
    (buffCh4M2,NumWFMCh4M2) = Parse_Channel(Chan4Mark2,'4M2',FullVariableString)
    maxBufLen4 = max([sum(buffChan4),sum(buffCh4M1),sum(buffCh4M2)])

    NumWFMs = max([NumWFMCh1,NumWFMCh1M1,NumWFMCh1M2])

    print('\nBuffer length calculate: %d, Waveform Length: %d' % (sum(buffChan1),WFM_length))
    print('---------------------------------------------------')
    print('POPULATING CHANNELS & MARKERS: %d waveforms, %d ns long' % (NumWFMs,WFM_length))
    (Chan1ArrVal) = Populate_Channel(Chan1Val,'1',FullVariableString,NumWFMs)
    (Chan1ArrMark1) = Populate_Marker(Chan1Mark1,'1M1',FullVariableString,NumWFMs)
    (Chan1ArrMark2) = Populate_Marker(Chan1Mark2,'1M2',FullVariableString,NumWFMs)

    (Chan2ArrVal) = Populate_Channel(Chan2Val,'2',FullVariableString,NumWFMs)
    (Chan2ArrMark1) = Populate_Marker(Chan2Mark1,'2M1',FullVariableString,NumWFMs)
    (Chan2ArrMark2) = Populate_Marker(Chan2Mark2,'2M2',FullVariableString,NumWFMs)

    (Chan3ArrVal) = Populate_Channel(Chan3Val,'3',FullVariableString,NumWFMs)
    (Chan3ArrMark1) = Populate_Marker(Chan3Mark1,'3M1',FullVariableString,NumWFMs)
    (Chan3ArrMark2) = Populate_Marker(Chan3Mark2,'3M2',FullVariableString,NumWFMs)

    (Chan4ArrVal) = Populate_Channel(Chan4Val,'4',FullVariableString,NumWFMs)
    (Chan4ArrMark1) = Populate_Marker(Chan4Mark1,'4M1',FullVariableString,NumWFMs)
    (Chan4ArrMark2) = Populate_Marker(Chan4Mark2,'4M2',FullVariableString,NumWFMs)

    FullChanArray = []

    FullChanArray.append(Chan1ArrVal)
    FullChanArray.append(Chan1ArrMark1)
    FullChanArray.append(Chan1ArrMark2)

    FullChanArray.append(Chan2ArrVal)
    FullChanArray.append(Chan2ArrMark1)
    FullChanArray.append(Chan2ArrMark2)

    FullChanArray.append(Chan3ArrVal)
    FullChanArray.append(Chan3ArrMark1)
    FullChanArray.append(Chan3ArrMark2)

    FullChanArray.append(Chan4ArrVal)
    FullChanArray.append(Chan4ArrMark1)
    FullChanArray.append(Chan4ArrMark2)

    return (FullChanArray,NumWFMs,WFM_length)

def Save_Sequence_File(FullChanArray,NumWFMs,WFM_length,FileName,FilePath):
    Chan1ArrVal = FullChanArray[0]
    Chan1ArrMark1 = FullChanArray[1]
    Chan1ArrMark2 = FullChanArray[2]

    Chan2ArrVal = FullChanArray[3]
    Chan2ArrMark1 = FullChanArray[4]
    Chan2ArrMark2 = FullChanArray[5]

    Chan3ArrVal = FullChanArray[6]
    Chan3ArrMark1 = FullChanArray[7]
    Chan3ArrMark2 =  FullChanArray[8]

    Chan4ArrVal = FullChanArray[9]
    Chan4ArrMark1 = FullChanArray[10]
    Chan4ArrMark2 = FullChanArray[11]

    numChans = 4


    base_filename = FileName
    LenData = len(Chan1ArrVal[0,:])*5
    LenHead = len(('%s' % LenData))

    base_dir = FilePath
    os.chdir(FilePath)
    basefile_dir = ('%s\\%s' %(base_dir,base_filename))
    print('---------------------------------------------------')
    print('SAVING FILES to %s' % basefile_dir)
    if not os.path.exists(basefile_dir):
        os.makedirs(base_filename)
        print ('Making subdirectory: %s' % base_filename)

    seq_name = os.path.join(basefile_dir,('AWG_SEQ_%s.seq' %(base_filename)))
    fseq = open(seq_name,'w')
    fseq.write('MAGIC 3004\n')
    fseq.write('LINES %s\n'% (NumWFMs))

    for wfm in range(0,NumWFMs):
        for cc in range(0,numChans):
            file_name = ('%s%dc%d.wfm' % (base_filename,wfm,cc+1))
            fseq.write(('"%s"' % file_name))
            if cc+1 != numChans:
                fseq.write(',')
            else:
                fseq.write((',0,0,%d,0\n' % (wfm+1)))
    fseq.write('JUMP_MODE SOFTWARE\n')
    fseq.write('JUMP_TIMING SYNC\n')
    fseq.write('CLOCK 1.0E+9')
    fseq.close()

    def write_waveform_files(ChanArrVal,ChanArrMark1,ChanArrMark2,ChanNum,NumWFMs):
        WFMfilenames = []
        WFMStrings = []
        for wfm in range(0,NumWFMs):
            WFMname = ('%s%dc%d' % (base_filename,wfm,ChanNum))
            file_name = ('%s.wfm' % (WFMname))
            WFMfilenames.append(WFMname)
            file_name = os.path.join(basefile_dir,file_name)
            fp = open(file_name,'w')
            fp.write('MAGIC 1000\n')
            fp.write('#%s%s'% (LenHead,LenData))
            WFMstring = ''
            for ii in range(0,WFM_length):
                WFMstring = WFMstring + struct.pack('<f',ChanArrVal[wfm,ii]) + struct.pack('<B',ChanArrMark1[wfm,ii]+2*ChanArrMark2[wfm,ii])
                fp.write(struct.pack('<f',ChanArrVal[wfm,ii]))
                fp.write(struct.pack('<B',ChanArrMark1[wfm,ii]+2*ChanArrMark2[wfm,ii]))
            fp.close()

        WFMStrings.append(WFMstring)

        print('SAVED WAVEFORMS for Chan%s' % ChanNum)
        return (WFMfilenames,WFMstring)

    (WFMChan1,WFMString1) = write_waveform_files(Chan1ArrVal,Chan1ArrMark1,Chan1ArrMark2,1,NumWFMs)
    (WFMChan2,WFMString2) = write_waveform_files(Chan2ArrVal,Chan2ArrMark1,Chan2ArrMark2,2,NumWFMs)
    (WFMChan3,WFMString3) = write_waveform_files(Chan3ArrVal,Chan3ArrMark1,Chan3ArrMark2,3,NumWFMs)
    (WFMChan4,WFMString4) = write_waveform_files(Chan4ArrVal,Chan4ArrMark1,Chan4ArrMark2,4,NumWFMs)


    return ([WFMChan1,WFMChan2,WFMChan3,WFMChan4],[WFMString1,WFMString2,WFMString3,WFMString4])

def Load_AWGDictFile():
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
##            print name_string
            AWG_Dict[name_string] = byte_string
            AWG_byte[name_string] = byte_num
            # Add to values dictionary, each entry containing the index (order in which read from file), byte length of data as stored on AWG, and value data itself
        except:
            break # Don't die on exception e.g. corrupt file or EOF, just break out of for loop

    fdict.close() # Close file

    return AWG_Dict


def Save_AWG_File(DesiredValues,AWG_Dict,FullChanArray,NumWFMs,WFM_length,FileName,FilePath):

    base_filename = FileName

    base_dir = FilePath
    os.chdir(base_dir)
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
            print ('%s %s %s' % (len(paramName.encode('UTF-8'))+1,paramName,eval(paramTypeCast)))
            fawg.write(struct.pack('<f',eval(paramTypeCast)))

        if paramDataType == 'float64': # populates of the value is a LONG
            fawg.write(struct.pack('<L',len(paramName.encode('UTF-8'))+1))
            fawg.write(struct.pack('<L',8))
            fawg.write('%s\x00' % (paramName))
            print ('%s %s %s' % (len(paramName.encode('UTF-8'))+1,paramName,eval(paramTypeCast)))
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
