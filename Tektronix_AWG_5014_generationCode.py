# Tek AWG program

import matplotlib
import numpy
import re
from pylab import *

AWG_model = '5014'

clock = 1 #ns
piPulse = 10 #ns

# CONSTANTS
WFM_length = 2500 # ns
GreenON = 1000 # ns
Green_AOM_delay = 1080 # ns

if AWG_model == '5014':
    print('Setting up for AWG %s' % AWG_model)
    numChans = 4
    numMrksPerChan = 2
elif AWG_model == '520':
    print('Setting up for AWG %s' % AWG_model)
    numChans = 2
    numMrksPerChan = 2

# times in ns
Chan1 = ['GreenON','600','numpy.linspace(0,600,51)','300']
Chan1m2 = ['WFM_length - Green_AOM_delay']

# will eventually be a function called interpretChan and interpretMarker
ChanCode = Chan1
ChanNum = 1
##print('Number of elements in Chan%s: %d\n' % (ChanNum,len(ChanCode)))

# Parse channel information
bufferLength = numpy.zeros(len(ChanCode))
print ('PARSING CHANNEL #%d, %d element(s)' % (ChanNum,len(ChanCode)))
NumWFMs = 1
for idx, element in enumerate(ChanCode):
##    print('%s: %s' % (idx, element))
    if element.isdigit():
        print('%d : Found constant digit, %d' % (idx,eval(element)))
        bufferLength[idx] = eval(element)
    else:
        if element.find('numpy') != -1:
            elementArr = eval(element) # cast array as integers
            bufferLength[idx] = max(elementArr)
            NumWFMs = len(elementArr)
            print('%d : Found numpy equation {%s} buffer length = %d, number of waveforms %d' % (idx,element,bufferLength[idx],NumWFMs))

        elif len(re.split('[-+*/]', element)) != 1:
            print ('%d : Found string equation, {%s} = %d' % (idx,element,eval(element)))
            bufferLength[idx] = eval(element)
        else:
            print('%d : Found string constant, %s = %d' % (idx,element,eval(element)))
            bufferLength[idx] = eval(element)

totalBuffLength = sum(bufferLength)
print('\nBuffer length calculate: %d, Waveform Length: %d' % (totalBuffLength,WFM_length))
print('---------------------------------------------------')
print('POPULATING CHANNEL #%d, %d waveforms, %d ns long' % (ChanNum,NumWFMs,WFM_length))


# Populate Channels
ChanArrVal = numpy.zeros(shape=(NumWFMs,WFM_length))

for wfm in range(0,NumWFMs):
    ChanArrIdx = 0 # reset Channel Array Index
    for idx, element in enumerate(ChanCode):
        if element.find('numpy') != -1:
            elementArr = numpy.int32(eval(element))
            bufferLength = max(elementArr)
            for x in range(0,elementArr[wfm]):
                ChanArrVal[wfm,ChanArrIdx+x] = 1
##                print('WFM %d: Chan%d, {%d, %s}' % (wfm,ChanNum,ChanArrIdx,ChanArrVal[wfm,x]))
            ChanArrIdx = ChanArrIdx+bufferLength
        else:
            for x in range(0,eval(element)):
                ChanArrVal[wfm,ChanArrIdx] = 0
##                print('WFM %d: Chan%d, {%d, %s}' % (wfm,ChanNum,ChanArrIdx,ChanArrVal[wfm,x]))
                ChanArrIdx = ChanArrIdx+1


# Plot one waveform
wfm = 1
Xdata = numpy.linspace(0,WFM_length,WFM_length)
Ydata = ChanArrVal[wfm,:]
plot(Xdata,Ydata)

xlabel('time (ns)')
ylabel('voltage (mV)')
title('Waveform %d' % wfm)
grid(True)
show()