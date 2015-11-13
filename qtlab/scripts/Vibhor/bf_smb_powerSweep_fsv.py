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
med.set_device('NeatDrum')
med.set_setup('BF,fsv,smb')
med.set_user('Vibhor')

print smb2.query('*IDN?')
print fsv.query('*IDN?')


####   EXP VARIABLES
cavity_freq=5900.585+36.236  # MHz
power_start=-20
power_stop=30
power_points=51

fsv_center_frequency= cavity_freq #cavity_freq 
fsv_span=  250*10^-6 #Wait time may have to adjusted if this number is changed
fsv_sweep_points = 101
fsv_BW=10*10^-6  #MHz


####### Preparing the SETUP
smb2.set_RF_frequency(cavity_freq)
smb2.set_RF_power(power_start)
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
#adwin.start_process()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_smb_powerSweep_fsv'
data = qt.Data(name=filename)
data.add_coordinate('smb power',size=power_points)
data.add_coordinate('fsv freq',size=fsv_sweep_points)
data.add_value('spectrum')

#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\neatDrum\\20140104\\')
data.copy_file('bf_smb_powerSweep_fsv.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
power_list=np.linspace(float(power_start),float(power_stop),power_points)
fsv_start=float(fsv_center_frequency)-float(fsv_span/2)
fsv_stop=float(fsv_center_frequency)+float(fsv_span/2)
fsv_list=np.linspace(fsv_start,fsv_stop,fsv_sweep_points)

print 'Start Experiments'

waittime=fsv.get_sweeptime()


for pw in power_list:
    pw_dummy=list(pw*ones(fsv_sweep_points))
    smb2.set_RF_power(pw)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current drive power ',pw
    qt.msleep(waittime+1)
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(pw_dummy,fsv_list,tr)
    spyview_process(data,fsv_start,fsv_stop,pw)


data.close_file()
qt.mend()
#end
