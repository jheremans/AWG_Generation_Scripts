# Tek AWG program
import matplotlib
import matplotlib.pyplot as plt
import numpy
import re
import sys
import os
import struct

os.chdir('C:\Users\Admin\Documents\GitHub\AWG_Generation_Scripts\Generation Codes from file')

def Parse_Channel(ChanCode,ChanNum,WFM_length):
# Parse channel information
    bufferLength = numpy.zeros(len(ChanCode)+1)
    ValBufferLength =numpy.zeros(len(ChanCode)+1)
    print ('PARSING CHAN%s, %d element(s)' % (ChanNum,len(ChanCode)))
    NumWFMs = 1
    NumValWFMs = 1
    for idx, element in enumerate(ChanCode):
        el_time = element[0]
        el_val = element[1]

        # Parse time values
        if el_time.isdigit():
            print('TIME %d : Found time constant digit, %d' % (idx,eval(el_time)))
            bufferLength[idx] = eval(el_time)
        else:
            if el_time.find('numpy') != -1:
                elementArr = eval(el_time) # cast array as integers
                bufferLength[idx] = max(elementArr)
                NumWFMs = len(elementArr)
                print('TIME %d : Found numpy equation {%s} buffer length = %d, number of waveforms %d' % (idx,el_time,bufferLength[idx],NumWFMs))

            elif len(re.split('[-+*/^]', el_time)) != 1:
                print ('TIME %d : Found string equation, {%s} = %d' % (idx,el_time,eval(el_time)))
                bufferLength[idx] = eval(el_time)
            else:
                print('TIME %d : Found string constant, %s = %d' % (idx,el_time,eval(el_time)))
                bufferLength[idx] = eval(el_time)


        # Parse values
        if (el_val == 'LOW'):
            print('%d : Found LOW digit' % (idx))
        elif (el_val == 'HIGH'):
            print('%d : Found HIGH digit' % (idx))

        else:
            if el_val.isdigit():
                        print('VALUE %d : Found value constant digit, %d' % (idx,eval(el_val)))
            elif el_val.find('numpy') != -1:
                elementArr = eval(el_val) # cast array as integers
                NumValWFMs = len(elementArr)
                print('VALUE %d : Found value numpy equation {%s} number of waveforms %d' % (idx,el_val,NumValWFMs))

            elif len(re.split('[-+*/^]', el_val)) != 1:
                print ('VALUE %d : Found value string equation, {%s} = %d' % (idx,el_val,eval(el_val)))
            else:
                print('VALUE %d : Found value string constant, %s = %d' % (idx,el_val,eval(el_val)))


    totalBufferLength = sum(bufferLength)
    if NumWFMs < NumValWFMs:
        NumWFMs = NumValWFMs

    bufferLength[idx+1] = WFM_length-totalBufferLength
    if bufferLength[idx+1] >= 0:
        print('NO PARSING ERRORS FOUND: Total Buffer Length = %s ns\n' % totalBufferLength)
        return (bufferLength,NumWFMs)
    else:
        print ('ERROR: total buffer length %s exceeds waveform length %s\n' % (totalBufferLength,WFM_length))
        sys.exit(0)


# Populate Channels
def Populate_Channel(ChanCode,ChanNum,WFM_length,NumWFMs):
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
                    if el_val.find('numpy') != -1:
                        elValArray = numpy.float(eval(el_val))
                        ChanArrVal[wfm,ChanArrIdx] = elValArray[wfm]
                    else:
                        ChanArrVal[wfm,ChanArrIdx+x] = eval(el_val)
                ChanArrIdx = ChanArrIdx+bufferLength
            else:
                for x in range(0,eval(el_time)):
                    if el_val.find('numpy') != -1:
                        elValArray = eval(el_val)
                        ChanArrVal[wfm,ChanArrIdx] = elValArray[wfm]
                        ChanArrIdx = ChanArrIdx+1
                    else:
                        ChanArrVal[wfm,ChanArrIdx] = eval(el_val)
                        ChanArrIdx = ChanArrIdx+1
    print('Populated Chan%s: NO ERRORS' % ChanNum)
    return ChanArrVal

# Populate Channels
def Populate_Marker(MarkerCode,ChanNum,WFM_length,NumWFMs):
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
                        print('HIGH WTF')
                    elif el_val == 'LOW':
                        MarkerArrVal[wfm,MarkerArrIdx] = 0
                    else:
                        print ('ERROR: unknown marker value')
                    MarkerArrIdx = MarkerArrIdx+1
    print('Populated Chan%s: NO ERRORS' % ChanNum)
    return MarkerArrVal


AWG_model = '5014'

clock = 1 #ns
piPulse = 10 #ns



if AWG_model == '5014':
    print('Setting up for AWG %s' % AWG_model)
    numChans = 4
    numMrksPerChan = 2
elif AWG_model == '520':
    print('Setting up for AWG %s' % AWG_model)
    numChans = 2
    numMrksPerChan = 2

# CONSTANTS
WFM_length = 10000 # ns

GreenAOMDelay = 1000
GreenPLread = 300
T_rabi =numpy.arange(0,601,10)
theta_vals = numpy.arange(-(numpy.pi),numpy.pi+.1,(numpy.pi)/16)
Iv = numpy.cos(theta_vals)
Qv = numpy.sin(theta_vals)
tstep = 200
atten = numpy.arange(0,1.03,0.03125)

# times in ns
Chan1Val = [('33*tstep','1'),('WFM_length-(33*tstep)','0')]
##[('tstep','Iv[0]'),('tstep','Iv[1]'),('tstep','Iv[2]'),('tstep','Iv[3]'),('tstep','Iv[4]'),('tstep','Iv[5]'),('tstep','Iv[6]'),('tstep','Iv[7]'),('tstep','Iv[8]'),('tstep','Iv[9]'),('tstep','Iv[10]'),('tstep','Iv[11]'),('tstep','Iv[12]'),('tstep','Iv[13]'),('tstep','Iv[14]'),('tstep','Iv[15]'),('tstep','Iv[16]'),('tstep','Iv[17]'),('tstep','Iv[18]'),('tstep','Iv[19]'),('tstep','Iv[20]'),('tstep','Iv[21]'),('tstep','Iv[22]'),('tstep','Iv[23]'),('tstep','Iv[24]'),('tstep','Iv[25]'),('tstep','Iv[26]'),('tstep','Iv[27]'),('tstep','Iv[28]'),('tstep','Iv[29]'),('tstep','Iv[30]'),('tstep','Iv[31]'),('WFM_length-160','0')]
Chan1Mark1 = [('WFM_length','LOW')]
Chan1Mark2 = [('WFM_length','LOW')]

Chan2Val = [('33*tstep','0'),('WFM_length-(33*tstep)','0')]
##[('tstep','Qv[0]'),('tstep','Qv[1]'),('tstep','Qv[2]'),('tstep','Qv[3]'),('tstep','Qv[4]'),('tstep','Qv[5]'),('tstep','Qv[6]'),('tstep','Qv[7]'),('tstep','Qv[8]'),('tstep','Qv[9]'),('tstep','Qv[10]'),('tstep','Qv[11]'),('tstep','Qv[12]'),('tstep','Qv[13]'),('tstep','Qv[14]'),('tstep','Qv[15]'),('tstep','Qv[16]'),('tstep','Qv[17]'),('tstep','Qv[18]'),('tstep','Qv[19]'),('tstep','Qv[20]'),('tstep','Qv[21]'),('tstep','Qv[22]'),('tstep','Qv[23]'),('tstep','Qv[24]'),('tstep','Qv[25]'),('tstep','Qv[26]'),('tstep','Qv[27]'),('tstep','Qv[28]'),('tstep','Qv[29]'),('tstep','Qv[30]'),('tstep','Qv[31]'),('WFM_length-160','0')]
Chan2Mark1 = [('WFM_length','LOW')]
Chan2Mark2 = [('WFM_length','LOW')]

Chan3Val = [('tstep','atten[0]'),('tstep','atten[1]'),('tstep','atten[2]'),('tstep','atten[3]'),('tstep','atten[4]'),('tstep','atten[5]'),('tstep','atten[6]'),('tstep','atten[7]'),('tstep','atten[8]'),('tstep','atten[9]'),('tstep','atten[10]'),('tstep','atten[11]'),('tstep','atten[12]'),('tstep','atten[13]'),('tstep','atten[14]'),('tstep','atten[15]'),('tstep','atten[16]'),('tstep','atten[17]'),('tstep','atten[18]'),('tstep','atten[19]'),('tstep','atten[20]'),('tstep','atten[21]'),('tstep','atten[22]'),('tstep','atten[23]'),('tstep','atten[24]'),('tstep','atten[25]'),('tstep','atten[26]'),('tstep','atten[27]'),('tstep','atten[28]'),('tstep','atten[29]'),('tstep','atten[30]'),('tstep','atten[31]'),('tstep','atten[32]'),('WFM_length-(33*tstep)','0')]
Chan3Mark1 = [('100','LOW'),('10','HIGH'),('WFM_length-110','LOW')]
Chan3Mark2 = [('WFM_length','LOW')]

Chan4Val = [('WFM_length','0')]
##[('3','0'),('tstep','Qv[0]'),('tstep','Qv[1]'),('tstep','Qv[2]'),('tstep','Qv[3]'),('tstep','Qv[4]'),('tstep','Qv[5]'),('tstep','Qv[6]'),('tstep','Qv[7]'),('tstep','Qv[8]'),('tstep','Qv[9]'),('tstep','Qv[10]'),('tstep','Qv[11]'),('tstep','Qv[12]'),('tstep','Qv[13]'),('tstep','Qv[14]'),('tstep','Qv[15]'),('tstep','Qv[16]'),('tstep','Qv[17]'),('tstep','Qv[18]'),('tstep','Qv[19]'),('tstep','Qv[20]'),('tstep','Qv[21]'),('tstep','Qv[22]'),('tstep','Qv[23]'),('tstep','Qv[24]'),('tstep','Qv[25]'),('tstep','Qv[26]'),('tstep','Qv[27]'),('tstep','Qv[28]'),('tstep','Qv[29]'),('tstep','Qv[30]'),('tstep','Qv[31]'),('WFM_length-163','0')]
Chan4Mark1 = [('WFM_length','LOW')]
Chan4Mark2 = [('WFM_length','LOW')]

# will eventually be a function called interpretChan and interpretMarker
ChanCode = Chan1Val
ChanNum = 1
##print('Number of elements in Chan%s: %d\n' % (ChanNum,len(ChanCode)))


# Parse channels
(buffChan1,NumWFMCh1) = Parse_Channel(Chan1Val,'1',WFM_length)
(buffCh1M1,NumWFMCh1M1) = Parse_Channel(Chan1Mark1,'1M1',WFM_length)
(buffCh1M2,NumWFMCh1M2) = Parse_Channel(Chan1Mark2,'1M2',WFM_length)
maxBufLen1 = max([sum(buffChan1),sum(buffCh1M1),sum(buffCh1M2)])

(buffChan2,NumWFMCh2) = Parse_Channel(Chan2Val,'2',WFM_length)
(buffCh2M1,NumWFMCh2M1) = Parse_Channel(Chan2Mark1,'2M1',WFM_length)
(buffCh2M2,NumWFMCh2M2) = Parse_Channel(Chan2Mark2,'2M2',WFM_length)
maxBufLen2 = max([sum(buffChan2),sum(buffCh2M1),sum(buffCh2M2)])

(buffChan3,NumWFMCh3) = Parse_Channel(Chan3Val,'3',WFM_length)
(buffCh3M1,NumWFMCh3M1) = Parse_Channel(Chan3Mark1,'3M1',WFM_length)
(buffCh3M2,NumWFMCh3M2) = Parse_Channel(Chan3Mark2,'3M2',WFM_length)
maxBufLen3 = max([sum(buffChan3),sum(buffCh3M1),sum(buffCh3M2)])

(buffChan4,NumWFMCh4) = Parse_Channel(Chan4Val,'4',WFM_length)
(buffCh4M1,NumWFMCh4M1) = Parse_Channel(Chan4Mark1,'4M1',WFM_length)
(buffCh4M2,NumWFMCh4M2) = Parse_Channel(Chan4Mark2,'4M2',WFM_length)
maxBufLen4 = max([sum(buffChan4),sum(buffCh4M1),sum(buffCh4M2)])



NumWFMs = max([NumWFMCh1,NumWFMCh1M1,NumWFMCh1M2,NumWFMCh2,NumWFMCh2M1,NumWFMCh2M2,NumWFMCh3,NumWFMCh3M1,NumWFMCh3M2,NumWFMCh4,NumWFMCh4M1,NumWFMCh4M2])

print('\nBuffer length calculate: %d, Waveform Length: %d' % (sum(buffChan1),WFM_length))
print('---------------------------------------------------')
print('POPULATING CHANNELS & MARKERS: %d waveforms, %d ns long' % (NumWFMs,WFM_length))
(Chan1ArrVal) = Populate_Channel(Chan1Val,'1',WFM_length,NumWFMs)
(Chan1ArrMark1) = Populate_Marker(Chan1Mark1,'1M1',WFM_length,NumWFMs)
(Chan1ArrMark2) = Populate_Marker(Chan1Mark2,'1M2',WFM_length,NumWFMs)

(Chan2ArrVal) = Populate_Channel(Chan2Val,'2',WFM_length,NumWFMs)
(Chan2ArrMark1) = Populate_Marker(Chan2Mark1,'2M1',WFM_length,NumWFMs)
(Chan2ArrMark2) = Populate_Marker(Chan2Mark2,'2M2',WFM_length,NumWFMs)

(Chan3ArrVal) = Populate_Channel(Chan3Val,'3',WFM_length,NumWFMs)
(Chan3ArrMark1) = Populate_Marker(Chan3Mark1,'3M1',WFM_length,NumWFMs)
(Chan3ArrMark2) = Populate_Marker(Chan3Mark2,'3M2',WFM_length,NumWFMs)

(Chan4ArrVal) = Populate_Channel(Chan4Val,'4',WFM_length,NumWFMs)
(Chan4ArrMark1) = Populate_Marker(Chan4Mark1,'4M1',WFM_length,NumWFMs)
(Chan4ArrMark2) = Populate_Marker(Chan4Mark2,'4M2',WFM_length,NumWFMs)
print('---------------------------------------------------')

print('SAVING FILES ')
base_dir = 'M:\Shared Projects\Cold Diamond\AWG'
base_filename = 'T_varyatten200ns_python'
os.chdir(base_dir)
LenData = len(Chan1ArrVal[0,:])*5
LenHead = len(('%s' % LenData))

basefile_dir = ('%s\\%s' %(base_dir,base_filename))
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
##            fseq.write((',0,0,%d,0\n' % (wfm)))

fseq.write('JUMP_MODE SOFTWARE\n')
fseq.write('JUMP_TIMING SYNC\n')
fseq.write('CLOCK 1.0E+9')
fseq.close()

def write_waveform_files(ChanArrVal,ChanArrMark1,ChanArrMark2,ChanNum,NumWFMs):
    for wfm in range(0,NumWFMs):
        file_name = ('%s%dc%d.wfm' % (base_filename,wfm,ChanNum))
        file_name = os.path.join(basefile_dir,file_name)
        fp = open(file_name,'w')
        fp.write('MAGIC 1000\n')
        fp.write('#%s%s'% (LenHead,LenData))
        for ii in range(0,WFM_length):
            fp.write(struct.pack('<f',ChanArrVal[wfm,ii]))
            fp.write(struct.pack('<B',ChanArrMark1[wfm,ii]+2*ChanArrMark2[wfm,ii]))
        fp.close()
    print('SAVED WAVEFORMS for Chan%s' % ChanNum)


write_waveform_files(Chan1ArrVal,Chan1ArrMark1,Chan1ArrMark2,1,NumWFMs)
write_waveform_files(Chan2ArrVal,Chan2ArrMark1,Chan2ArrMark2,2,NumWFMs)
write_waveform_files(Chan3ArrVal,Chan3ArrMark1,Chan3ArrMark2,3,NumWFMs)
write_waveform_files(Chan4ArrVal,Chan4ArrMark1,Chan4ArrMark2,4,NumWFMs)

# Plot one waveform
##f = figure()
##graph1 = f.add_subplot(311)
##graph2 = f.add_subplot(312,sharex=graph1)
##graph3 = f.add_subplot(313,sharex=graph1)
##nb = 1

##KBinput = raw_input('What waveform would you like')
##decoded = KBinput.decode('utf-8')
##inputWFM = decoded.encode('utf-8')
##print('Desire WFM %s',inputWFM)



##while (inputWFM != 'q'):
##    if inputWFM != 'q':
##        graph1.clear()
##        graph2.clear()
##        graph3.clear()
##
##        wfm = eval(inputWFM)
##        Xdata = numpy.linspace(0,WFM_length,WFM_length)
##        Ydata = ChanArrVal[wfm,:]
##
##        graph1.plot(Xdata,Ydata)
##        graph1.set_title('Waveform %d' % wfm)
##        graph1.set_ylabel('Channels voltage (mV)')
##        grid(True)
##        graph2.plot(Xdata,Ydata)
##
##
##
##        graph2.plot(Xdata,Ydata)
##        graph2.set_ylabel('Chan 1 & 2 Markers voltage (mV)')
##
##
##        graph3.plot(Xdata,Ydata)
##        graph3.set_ylabel('Chan 3& 4 Markers voltage (mV)')
##
##
##        xlabel('time (ns)')
##        ylabel('voltage (mV)')
##        show()
##
##
##print('Quit detected')

fig = plt.figure(figsize=(5,10))

plt.imshow(Chan1ArrVal, aspect="auto",cmap=plt.get_cmap('BuGn'))

##plt.show()

