################################
#       DESCRIBTION
################################

#Measurement script that does single tone qubit spectroscopy using the ADwin
#as a DAC to either sweep magnetic field of gate voltage.


################################
#       DEVELOPMENT NOTES/LOG
################################


#transform into virtual spectrum analyser module




################################
#      IMPORTS
################################

import qt
import numpy as np
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen2D.py')


################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec

#1st coordinate
start_frequency= 7145
stop_frequency= 7200
##f_points =101


#2nd coordinate
start_magvoltage =0
stop_magvoltage = 1.3
magv_points = 200

magvlist=np.linspace(float(start_magvoltage),float(stop_magvoltage),magv_points)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV',address='TCPIP::192.168.1.101::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS3_minitransmon')
med.set_setup('BF')
med.set_user('Sal')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')



#FSV instrument variables
#This script assumes that the signal analyser is already setup with the SMB100A tracking generator
kHz=0.001
fsv_bandwidth = 50*kHz     #MHz
#fsv_bandwidth = 1     #MHz

fsv_source_power =-20


fsv.set_resolution_bandwidth(fsv_bandwidth)
fsv.set_start_frequency(start_frequency)
fsv.set_stop_frequency(stop_frequency)

#start_frequency = 2000
#stop_frequency=5000
sweeppoints = 1001
fsv.set_sweeppoints(sweeppoints)

sweep_runs = 1
trace_len=fsv.get_sweeppoints()
flist=np.linspace(float(start_frequency),float(stop_frequency),sweep_runs*trace_len)
sweeplist=np.linspace(start_frequency,stop_frequency,sweep_runs)

f_points=sweep_runs*sweeppoints
fsv.set_sweeppoints(f_points)




#fsv.set_trace_continuous(False)

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_single_tone_2D'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('Magnet Voltage (V)')
data.add_value('transmission (dBm)')

data.create_file(file)
data.copy_file('bf_single_tone_hres_2D.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=1) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
tstart = time()

x_time = 0
y_temp =0
measurement_time=0

print 'Start Experiment'

#while (x_time < max_runtime or  and run_index<norm_runs):


print 'Set magnet to starting point and wait several seconds'

adwin.set_DAC_2(magvlist[0])
qt.msleep(10)

for magv in magvlist:

    x_time = time()

    #Set Voltage
    adwin.set_DAC_2(magv)

    
        
    qt.msleep(1)

    #Do hres trace
    sweep_index=0
    trace=[]
    while(sweep_index<sweep_runs):
        print magv
        fsv.set_start_frequency(flist[sweep_index*trace_len])
        fsv.set_stop_frequency(flist[(sweep_index+1)*trace_len-1])
        trace.extend(fsv.get_trace())
        sweep_index+=1
                               
    data.add_data_point(flist, list(magv*ones(len(flist))),trace)

    data.new_block()
    spyview_process(data,start_frequency,stop_frequency,magv)
    qt.msleep(0.01) #wait 10 usec so save etc

##        index=0
##    for f in flist:
##        print 'frequency [MHz]', f, trace[index],v
##        index=index+1
data.close_file()
adwin.set_DAC_2(0)
qt.mend()
#end of experiment routine

