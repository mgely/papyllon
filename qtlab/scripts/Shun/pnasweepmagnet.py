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

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::192.168.1.42::inst0::INSTR')

#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('dcsquid')
med.set_setup('BF')
med.set_user('Shun')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'pnasweepmagnet'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('adwin[V]')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 [X]')
data.add_value('S21 [Y]')
#data.create_file()

base_path = 'D:\\data\\Shun\\dcsquid\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('pnasweepmagnet.py')




kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature

#14 mK


pow_start=-12
f1_pts = 1001
f1_bw = 1000 #HZ
f1_start=5200*MHz # hanger_f0-hanger_span/2
f1_stop= 5700*MHz #hanger_f0+hanger_span/2

### Gate settings
#adwin.start_process()
## Voltage mode with 100uV scale SYMM
##single, V+R mode
gate_start=0.30;
gate_stop=0.6;
gate_pt=101;

########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
gate_list=np.linspace(gate_start,gate_stop,gate_pt)
#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=f1_start,stop_frequency=f1_stop, sweeppoints=(f1_pts),bandwidth=f1_bw,level=pow_start)
pna.get_all() #get all the settings and store it in the settingsfile.
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
# for speed turn off display 
# use 32bit data

####   EXPERIMENTAL AREA  ##########
print 'set experimental stuf, point averages, ...'
pna.set_averages_off()
#pna.set_averages(4)
#pna.w('SENS:AVER:MODE POIN') #for testing! set averaging mode to points (all chanals) sweep is the other option

#do a PNA testsweep
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
#pna.sweep()

######################################

########## Print settings ################

print 'step size: '+str((f1_stop-f1_start)/(f1_pts-1)) +' Hz'
print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
print 'averages of the pna: '+str(pna.get_averages())
print 'sweeptime per trace (sec): '+str(sweep_time)

##################################################

print 'measurement loop:'

tstart = time()
prev_time=tstart
now_time=0
pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)
qt.msleep(0.1)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
for gt in gate_list:
    adwin.set_DAC_2(gt)
    print 'Gate value ADWIN '+str(gt)+' Volt'
    qt.msleep(3)
    pna.sweep()

    trace= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    gt_dummy=np.linspace(gt,gt,len(f_list))
    data.add_data_point(gt_dummy,f_list,trace[0],trace[1],trace2[0],trace2[1])
    data.new_block()
    spyview_process(data,f1_start,f1_stop,gt)
    qt.msleep(0.01)
data.close_file()
adwin.set_DAC_2(0)
qt.mend()



