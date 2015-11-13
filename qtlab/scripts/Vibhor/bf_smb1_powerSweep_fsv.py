import qt
import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')

####   EXP VARIABLES

### AdWIN 4V

gate=1


cavity_freq=5930.119  # MHz
cavity_level=16 # dBm with Vari att 1-6 and three splitter arms 3 dBm each

#Drive SMB 100A

start_frequency= 39.462  # MHz

power_start=-30
power_stop=-70
power_points=41

#stop_frequency= 61
#sweep_points = 1001
rf_power=-30

fsv_center_frequency= cavity_freq #cavity_freq # Unit is MHZ here
fsv_span=  85 #2*stop_frequency #MHz Wait time may have to adjusted if this number is changed
fsv_sweep_points = 2001
fsv_BW=2*10^-5  #MHz

#adwin_sweeptime=2 #sec

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136::inst0::INSTR')
    
if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.1.25::INSTR')

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')

if 'adwin' not in instlist:
    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('uglyDrum')
med.set_setup('BF,fsv,smb')
med.set_user('Vibhor')

print smb.query('*IDN?')
print fsv.query('*IDN?')

####### Preparing the SETUP
    #Cavity 
#smb2.set_RF_frequency(cavity_freq)
#smb2.set_RF_power(cavity_level)
#smb2.set_RF_state(True)
    #Drive smb
#smb.reset()
smb.set_RF_power(rf_power)
smb.set_RF_frequency(start_frequency)
smb.set_RF_state(True)

#fsv.reset()
fsv.set_center_frequency(fsv_center_frequency)
fsv.set_span(fsv_span)
fsv.set_resolution_bandwidth(fsv_BW)
fsv.set_sweeppoints(fsv_sweep_points)

####  ADWIN
#adwin.set_DAC_2(gate)
#while abs(adwin.get_DAC_2()-gate)>0.1:
#    qt.msleep(2)
#qt.msleep(adwin_sweeptime)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#adwin.start_process()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_smb1_powerSweep_fsv'
data = qt.Data(name=filename)
data.add_coordinate('smb power',size=power_points)
data.add_coordinate('fsv freq',size=fsv_sweep_points)
data.add_value('spectrum')

data.create_file()
data.copy_file('bf_smb1_powerSweep_fsv.py')

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
    smb.set_RF_power(pw)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current drive power ',pw
    qt.msleep(waittime+4)
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(pw_dummy,fsv_list,tr)
    spyview_process(data,fsv_start,fsv_stop,pw)


data.close_file()
qt.mend()
#end
