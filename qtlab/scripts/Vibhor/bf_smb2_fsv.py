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


# Cavity drive with smb2  with 8 dB power on top -35 on device

start_frequency= 5931.41-0.2
stop_frequency= 5931.41+0.2
sweep_points = 101
rf_power=26

fsv_center_frequency=start_frequency # Unit is MHZ here
fsv_span= 0.000050 #MHz Wait tim emay have to adjusted if this number is changed
fsv_sweep_points = 101
fsv_BW=5e-6

#SMB2 100A instrument
#smb2.reset()
smb2.set_RF_power(rf_power)
smb2.set_RF_frequency(start_frequency)
smb2.set_RF_state(True)

#fsv.reset()
fsv.set_center_frequency(start_frequency)
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
filename = 'bf_smb2_fsv'
data = qt.Data(name=filename)
data.add_coordinate('smb freq',size=sweep_points)
data.add_coordinate('fsv freq',size=fsv_sweep_points)
data.add_value('spectrum')

#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\post-Trieste\\20131020\\')
data.copy_file('bf_smb2_fsv.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_points)

#fsv_start=float(fsv_center_frequency)-float(fsv_span)
#fsv_stop=float(fsv_center_frequency)+float(fsv_span)
#fsv_list=np.linspace(fsv_start,fsv_stop,fsv_sweep_points)
fsv_list=np.linspace(0,501,fsv_sweep_points)
print 'Start Experiments'

waittime=fsv.get_sweeptime()


for freq in flist:
    freq_dummy=list(freq*ones(fsv_sweep_points))
    smb2.set_RF_frequency(freq)
    fsv.set_center_frequency(freq)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current drive frequency ',freq
    qt.msleep(waittime+1.5)
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(freq_dummy,fsv_list,tr)
    spyview_process(data,0,501,freq)

data.close_file()
qt.mend()
#end
