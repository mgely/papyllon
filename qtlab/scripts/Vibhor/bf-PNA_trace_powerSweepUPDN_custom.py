#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
#execfile('metagen3D_crazy.py')
execfile('metagen.py')

    
#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "installed instruments: "+" ".join(instlist)
#install the drivers no check

if 'med' not in instlist:
    med = qt.instruments.create('med','med')
#if 'pna' not in instlist:
#    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('uglyDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'S21_powerSweep_UPDN_custom'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Power [dBm]')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')
#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\post-Trieste\\20131022\\')
data.copy_file('bf-PNA_trace_powerSweepUPDN_custom.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#T 13 mK
# Gate = 3.12 / 4 V
# Cavity2 at carrier optimum number 5931.35 with 23 dBm - 10dB(dir coup)-6 (att)-10 dir coup(-37 on device)
## VNA drive has 20 + 8 + 37 inside
# LO tuned to 13 dBm ## CHECK THE log book for getting the right level at LO
## HEMT (37) + blue + cancel + miteq -16 att  + miteq + minickt 
## Complicated carrier cancellation scheme see Log book entry 21 7 13 for the setup

##
pow_start=3
pow_stop=-30
pow_pt=34
f1_pts = 501
f1_bw = 1 #HZ
pna.set_power(pow_start)
pna.set_resolution_bandwidth(f1_bw)

probe_f0=(40.75)*MHz
probe_span=0.8*MHz
f1_start=probe_f0-probe_span/2
f1_stop=probe_f0+probe_span/2
probe_pt=f1_pts


## Forward and backward sweep
## All settings needs to be set manually
## Here many points are for logging only

pna.w('SENS:FOM:RANG:SEGM1:FREQ:STAR '+str(f1_start))
pna.w('SENS:FOM:RANG:SEGM1:FREQ:STOP '+str(f1_stop))
pna.w('SENS:FOM:RANG:SEGM1:SWE:POIN '+str(probe_pt))
pna.w('SENS:FOM:RANG:SEGM2:FREQ:STAR '+str(f1_stop))
pna.w('SENS:FOM:RANG:SEGM2:FREQ:STOP '+str(f1_start))
pna.w('SENS:FOM:RANG:SEGM2:SWE:POIN '+str(probe_pt))


#adwin.start_process()
#adwin.set_DAC_2(3.12/4)

########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
rev=f_list[::-1]
comb_f_list = []
comb_f_list.extend(f_list)
comb_f_list.extend(rev)
pow_list=np.linspace(pow_start,pow_stop,pow_pt)
#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'


######################################

########## Print settings ################

#print 'step size: '+str((f1_stop-f1_start)/(f1_pts-1)) +' Hz'
#print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
#print 'averages of the pna: '+str(pna.get_averages())
#print 'sweeptime per trace (sec): '+str(sweep_time)

##################################################

print 'measurement loop:'

#pna.set_start_frequency(f1_start)
#pna.set_stop_frequency(f1_stop)
qt.msleep(0.1)
#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
for pw in pow_list:
    pna.set_power(pw)
    pna.set_power(pw)
    if -30<= pw < -25:
        bandw=10
    elif -25<= pw <-20:
        bandw=20
    elif -20<= pw <-15:
        bandw=30
    elif -15<= pw <0:
        bandw=50
    else:
        bandw=100
    pna.set_resolution_bandwidth(bandw)
    print 'Power NOW   '+str(pw)
    pna.sweep()
    #qt.msleep(sweep_time)
    trace1= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    pw_dummy=np.linspace(pw,pw,len(comb_f_list))
    data.add_data_point(pw_dummy,comb_f_list,trace1[0],trace1[1],trace2[0],trace2[1]) #for S21 vs power
    data.new_block()
    spyview_process(data,1,1002,pw)
    qt.msleep(0.01)

#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
data.close_file()
qt.mend()
