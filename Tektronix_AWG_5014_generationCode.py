# Tek AWG program

##import matplotlib
import numpy
import re

AWG_model = '5014'

clock = 1 #ns
piPulse = 10 #ns

# CONSTANTS
WFM_length = 4000 # ns
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
Chan1 = ['GreenON','600','numpy.linspace(10,200,20)']
Chan1m2 = ['WFM_length - Green_AOM_delay']

# will eventually be a function called interpretChan and interpretMarker
ChanCode = Chan1m2
ChanNum = 1
##print('Number of elements in Chan%s: %d\n' % (ChanNum,len(ChanCode)))

ChanArrVal = numpy.zeros(shape=(WFM_length))
ChanArrIdx = 0

print ('PARSING CHANNEL #%d, %d element(s)' % (ChanNum,len(ChanCode)))
for idx, element in enumerate(ChanCode):
##    print('%s: %s' % (idx, element))
    if element.isdigit():
        print('%d : Found constant digit, %d' % (idx,eval(element)))
##        for x in range(0,eval(element)):
##            ChanArrIdx = ChanArrIdx+1
##            ChanArrVal = 1
##            print('SetVal to Char%d, Idx: %d, Val: %s' % (ChanNum,ChanArrIdx,ChanArrVal))
    else:
##        print('Found a string: %s' % element)
        if element.find('numpy') != -1:
            elementArr = eval(element)
            bufferLength = max(elementArr)
            NumWaveforms = len(elementArr)
            print('%d : Found numpy equation {%s} buffer length = %d, number of waveforms %d' % (idx,element,bufferLength,NumWaveforms))

        elif len(re.split('[-+*/]', element)) != 1:
            print ('%d : Found string equation, {%s} = %d' % (idx,element,eval(element)))
        else:
            print('%d : Found string constant, %s = %d' % (idx,element,eval(element)))
##            for x in range(0,eval(element)):
##                        ChanArrIdx = ChanArrIdx+1
##                        ChanArrVal = 1
##                        print('SetVal to Char%d, Idx: %d, Val: %s' % (ChanNum,ChanArrIdx,ChanArrVal))