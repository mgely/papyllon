import qt
import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136::inst0::INSTR')
    
if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('UglyDrum')
med.set_setup('BF,fsv,smb2')
med.set_user('Vibhor')

print smb2.query('*IDN?')
print fsv.query('*IDN?')

start_power= -10
stop_power= 30
sweep_points = 41
rf_freq=5864.344

fsv_center_frequency=rf_freq # Unit is MHZ here
fsv_span= 0.000250 #MHz Wait tim emay have to adjusted if this number is changed
fsv_sweep_points = 151
fsv_BW=2e-5

## Atte dir coup direct  +dircoup direct + 37 (inside) 4th Feb entry
## PNA OFF
## output HEMT + blue cable + dir coup direct + fsv
#SMB2 100A instrument
#smb2.reset()
smb2.set_RF_power(start_power)
smb2.set_RF_frequency(rf_freq)
smb2.set_RF_state(True)

#fsv.reset()
fsv.set_center_frequency(fsv_center_frequency)
fsv.set_span(fsv_span)
fsv.set_resolution_bandwidth(fsv_BW)
fsv.set_sweeppoints(fsv_sweep_points)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'Power_sweep_blue'
data = qt.Data(name=filename)
data.add_coordinate('smb2 power',size=sweep_points)
data.add_coordinate('fsv freq',size=fsv_sweep_points)
data.add_value('spectrum')

#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\neatDrum\\20140206\\')
data.copy_file('bf_smb2-fsv-power.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
plist=np.linspace(float(start_power),float(stop_power),sweep_points)

fsv_start=fsv_center_frequency*1e6-fsv_span*1e6/2
fsv_stop=fsv_center_frequency*1e6+fsv_span*1e6/2
fsv_list=np.linspace(fsv_start,fsv_stop,fsv_sweep_points)

print 'Start Experiments'
waittime=fsv.get_sweeptime()

for pw in plist:
    pw_dummy=list(pw*ones(fsv_sweep_points))
    smb2.set_RF_power(pw)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current power ',pw
    qt.msleep(waittime+3)
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(pw_dummy,fsv_list,tr)
    spyview_process(data,fsv_start,fsv_stop,pw)

data.close_file()
qt.mend()
#end
