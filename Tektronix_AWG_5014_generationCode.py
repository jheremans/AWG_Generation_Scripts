# Tek AWG program

import matplotlib
import matplotlib.pyplot as plt
import numpy
import re
import sys

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
Chan1m2 = ['']


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

plt.imshow(ChanArrVal, aspect="auto",cmap=plt.get_cmap('BuGn'))

plt.show()