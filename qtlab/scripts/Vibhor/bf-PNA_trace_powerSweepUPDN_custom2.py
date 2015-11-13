# drive power = 23 dBm raw

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

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'LowPower'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Power [dBm]')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')
base_path = 'D:\\data\\Vibhor\\NeatDrum post highPower\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('bf-PNA_trace_powerSweepUPDN_custom2.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#T 13 mK
## 0V gate, See log book entry 15-10-14

pow_start=18
pow_stop=-6
pow_pt=25
f1_pts = 1001
f1_bw = 100 #HZ
pna.set_power(pow_start)
pna.set_resolution_bandwidth(f1_bw)

probe_f0=(5900.5435)*MHz
probe_span=0.02500*MHz
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
    if -6<= pw < 0:
        bandw=10
    elif 0<= pw <6:
        bandw=30
    elif 6<= pw <12:
        bandw=50
    elif 12<= pw <=18:
        bandw=100
    else:
        bandw=100
    

    print 'Power NOW   '+str(pw)+'  BW =  '+str(bandw)
    pna.set_resolution_bandwidth(bandw)
    pna.sweep()
    #qt.msleep(sweep_time)
    trace1= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    pw_dummy=np.linspace(pw,pw,len(comb_f_list))
    data.add_data_point(pw_dummy,comb_f_list,trace1[0],trace1[1],trace2[0],trace2[1]) #for S21 vs power
    data.new_block()
    spyview_process(data,1,2002,pw)
    qt.msleep(0.01)

#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
data.close_file()
qt.mend()
