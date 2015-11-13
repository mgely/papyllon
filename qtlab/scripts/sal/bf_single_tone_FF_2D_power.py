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
import visa
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

kHz = 1e3
MHz = 1e6
GHz = 1e9

pinit=-45
bw=30
f_start=5.272*GHz
f_stop=5.3
72*GHz
f_pts=401


#other settings



### Variables for power
p_start = -45
p_stop =0
p_pts =10

f_list=np.linspace(f_start,f_stop,f_pts)
#v_list=np.linspace(v_start,v_stop,v_pts)
p_list = np.linspace(p_start,p_stop,p_pts)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_single_tone_FF_2D_power'
data = qt.Data(name=filename)
data.add_coordinate('Frequency [MHz]')
data.add_coordinate('Power [dBm]')
data.add_value('S21 [abs]')
#data.add_value('S21 [rad]')


basepath = 'D:\\data\\Sal\\EOS8_C\\'

now = localtime()
datepath = str(now.tm_year) + str(now.tm_mday) + str(now.tm_mon) + '\\'

data.create_file(name=filename, datadirs=basepath+datepath+filename)
data.copy_file('bf_single_tone_FF_2D_power.py')




################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'ff' not in instlist:
    ff = qt.instruments.create('ff','universal_driver', address='TCPIP::192.168.1.151::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS8_C')
med.set_setup('BF')
med.set_user('Sal & Vibhor')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')


#setting of the Field Fox

##ff.write('*RST;*OPC?')                    #reset instrument
##qt.msleep(10)
##ff.write('INITiate:CONTinuous OFF') #switch off cont sweep
##ff.write('INST:SEL "NA";*OPC?')           #switch FF to NA mode
##ff.write('CALC:FORM MLOG')          #set measurement type to MLOG
##ff.write('CALC:PAR:DEF S21 \r')     #set S21 measurement
##
##ff.write('FREQ:STAR '+str(start_freq)+ '\n')
##ff.write('FREQ:STOP '+str(stop_freq)+ '\n')
##ff.write('BWID ' + str(bandwidth) + '\n')
##ff.write('SOUR:POW ' + str(start_power) + '\n')
##ff.write('SWE:POIN ' + str(f_points) + '\n')
##

ff.write('*RST')

qt.msleep(20)

ff.write('INST:SEL "NA";*OPC?')
ff.write('FREQ:STOP '+str(f_stop)+'\n')
ff.write('FREQ:STAR '+str (f_start)+'\n')
ff.write('BWID '+str(bw)+'\n')
ff.write('SOUR:POW '+str(pinit)+'\n')
ff.write('SWE:POIN '+str(f_pts)+'\n')
ff.write('CALC:PAR:DEF S21 \r')




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

def display_time(time):
    hours = time/3600
    minutes = (time-3600*floor(hours))/60
    seconds = (time-3600*floor(hours)-60*floor(minutes))

    return hours, ':', minutes, ':', seconds
    

#variables
run_index=0
tstart = time()
averages=1

prev_time=tstart
now_time=0
exp_number = len(p_list)

qt.msleep(15)

for p in p_list:

    now_time = time()
    time_int = now_time-prev_time
    prev_time = now_time
    
    exp_time = exp_number*time_int
    if exp_time<0:
        exp_time = 60

    ave_list = np.linspace(1,averages,averages)
    
##    print 'power: ' + str(p)
##    ff.write('SOUR:POW ' +str(p) + '\n')
##    print ff.query('SOUR:POW?')
##
##    qt.msleep(0.1)
##
##    ##for averaging one could use 'AVER:COUN' and clear avereging again with 'AVER:CLE'
##    #do trace and wait
##    ff.write('INIT:IMM;*OPC?')
##
##    qt.msleep(10)
##
##    #ff.write('CALC:FORM MLOG \r')
##    trace_mlog = eval(ff.query('CALC:DATA:FDAT?'))

    print 'current power '+str(p)+' power'
    ff.write('SOUR:POW ' +str(p)+'\n')
    print ff.query('SOUR:POW?')
   #adwin.set_DAC_2(v)
    qt.msleep(2)
    #setting tarce 1
    ff.write('INIT \r')
    qt.msleep(35)
    ff.write('CALC:FORM MLOG \r')
    qt.msleep(2)
    trace_mlog = eval(ff.query('CALC:DATA:FDAT? \r'))
    qt.msleep(1)

    v_dummy=np.linspace(p,p,len(f_list))
    data.add_data_point(v_dummy,f_list,trace_mlog)

    data.new_block()
    spyview_process(data,f_start,f_stop,p)
    qt.msleep(0.01) #wait 10 usec so save etc

data.close_file()
qt.mend()
#end of experiment routine

