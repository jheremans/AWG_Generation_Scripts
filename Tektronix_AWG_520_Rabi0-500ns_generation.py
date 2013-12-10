# Tek AWG program
import matplotlib
import matplotlib.pyplot as plt
import numpy
import re
import sys
import os
import struct

os.chdir('C:\Users\Felix\Documents\GitHub')

def Parse_Channel(ChanCode,ChanNum,WFM_length):
# Parse channel information
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
                    ChanArrVal[wfm,ChanArrIdx+x] = eval(el_val)
                ChanArrIdx = ChanArrIdx+bufferLength
            else:
                for x in range(0,eval(el_time)):
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
##                        print('No Numpy Found: %s, HIGH' % wfm)
                    elif el_val == 'LOW':
                        MarkerArrVal[wfm,MarkerArrIdx] = 0
##                        print('No Numpy Found: %s, LOW' % wfm)
                    else:
                        print ('ERROR: unknown marker value')

                    MarkerArrIdx = MarkerArrIdx+1

    print('Populated Chan%s: NO ERRORS' % ChanNum)
    return MarkerArrVal


AWG_model = '520'

clock = 1 #ns
piPulse = 10 #ns


# CONSTANTS
WFM_length = 2500 # ns

if AWG_model == '5014':
    print('Setting up for AWG %s' % AWG_model)
    numChans = 4
    numMrksPerChan = 2
elif AWG_model == '520':
    print('Setting up for AWG %s' % AWG_model)
    numChans = 2
    numMrksPerChan = 2

GreenAOMDelay = 1000
GreenPLread = 300
T_rabi =numpy.arange(0,601,10)

# times in ns
Chan1Val = [('WFM_length','0')]
Chan1Mark1 = [('WFM_length-GreenAOMDelay','LOW'),('GreenAOMDelay','HIGH')]
Chan1Mark2 = [('WFM_length','LOW')]

Chan2Val = [('WFM_length','0')]
Chan2Mark1 = [('GreenAOMDelay','LOW'),('600','LOW'),('numpy.arange(0,601,10)','HIGH'),('300','LOW')]
Chan2Mark2 = [('WFM_length','LOW')]


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


NumWFMs = max([NumWFMCh1,NumWFMCh1M1,NumWFMCh1M2,NumWFMCh2,NumWFMCh2M1,NumWFMCh2M2])

print('\nBuffer length calculate: %d, Waveform Length: %d' % (sum(buffChan1),WFM_length))
print('---------------------------------------------------')
print('POPULATING CHANNELS & MARKERS: %d waveforms, %d ns long' % (NumWFMs,WFM_length))
(Chan1ArrVal) = Populate_Channel(Chan1Val,'1',WFM_length,NumWFMs)
(Chan1ArrMark1) = Populate_Marker(Chan1Mark1,'1M1',WFM_length,NumWFMs)
(Chan1ArrMark2) = Populate_Marker(Chan1Mark2,'1M2',WFM_length,NumWFMs)

(Chan2ArrVal) = Populate_Channel(Chan2Val,'2',WFM_length,NumWFMs)
(Chan2ArrMark1) = Populate_Marker(Chan2Mark1,'2M1',WFM_length,NumWFMs)
(Chan2ArrMark2) = Populate_Marker(Chan2Mark2,'2M2',WFM_length,NumWFMs)
print('---------------------------------------------------')
print('SAVING FILES ')

base_filename = 'AWG520_T_Rabi0-600_python'
LenData = len(Chan1ArrVal[0,:])*5
LenHead = len(('%s' % LenData))

base_dir = 'M:\Shared Projects\Cold Diamond\AWG'
os.chdir(base_dir)
basefile_dir = ('%s\\%s' %(base_dir,base_filename))
if not os.path.exists(basefile_dir):
    os.makedirs(base_filename)
    print ('Making subdirectory: %s' % base_filename)

seq_name = os.path.join(basefile_dir,('AWG520_SEQ_%s.seq' %(base_filename)))
fseq = open(seq_name,'w')
fseq.write('MAGIC 3002\n')
fseq.write('LINES %s\n'% (NumWFMs))

for wfm in range(0,NumWFMs):
    for cc in range(0,numChans):
        file_name = ('%s%dc%d.wfm' % (base_filename,wfm,cc+1))
        fseq.write(('"%s"' % file_name))
        if cc+1 != numChans:
            fseq.write(',')
        else:
            fseq.write((',0,1,%d,0\n' % (wfm+1)))
fseq.write('LOGIC_JUMP 1,-1,-1,-1\n')
fseq.write('JUMP_MODE SOFTWARE\n')
fseq.write('JUMP_TIMING SYNC\n')
##fseq.write('CLOCK 1.0E+9')
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
        fp.write('CLOCK 1.0E+9')
        fp.close()
    print('SAVED WAVEFORMS for Chan%s' % ChanNum)


write_waveform_files(Chan1ArrVal,Chan1ArrMark1,Chan1ArrMark2,1,NumWFMs)
write_waveform_files(Chan2ArrVal,Chan2ArrMark1,Chan2ArrMark2,2,NumWFMs)

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

