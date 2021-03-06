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
#execfile('metagen2D.py')
execfile('metagen3D.py')



################################
#      VARIABLES
################################

#For internal instrument variables see instruments section


#Core variables
f_points =3001
bandwidth=200
power = 20
averages=1

h_1=4.44e9
h_2=5.176e9
h_3=6.2689e9
h_4=8.55e9

f_estimate=h_1
span=200.e6

start_freq=3.5e9
stop_freq=9.5e9

#start_freq=f_estimate-span/2
#stop_freq=f_estimate+span/2

flist=np.linspace(float(start_freq),float(stop_freq),f_points)



start_magv=-10
stop_magv=10
#mag_d = 0.25
#magv_points = int((stop_magv - start_magv+1)/mag_d)

magv_points = 201
magvlist=np.linspace(float(start_magv),float(stop_magv),magv_points)

iteration=np.linspace(1,1,3)

power_list=[-30,-27,-24,-21,-18,-15,-12,-9,-6,-3,0,3,6,9]



################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#if 'adwin_DAC' not in instlist:
#    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

pna_IF_list=[1,2,3,5,7,10,15,20,30,50,70,100,150,200,300,500,700,1e3,1.5e3,2e3,3e3,5e3,7e3,10e3,15e3,20e3]

pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq,measurement_format = 'MLOG')
pna.set_power(power)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
pna.set_averages_on()
pna.set_averages(averages)
sweeptime = pna.get_sweeptime()*1.05

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program
#adwin.set_rampsteps(100)
#adwin.set_DAC_1(0)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Sal\\LETO11V_10mK\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed



#Set up data
filename = 'hanger_single_tone_PNA_3D_power_magramp_quick_scan'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('power (dBm)')
data.add_coordinate('V_adwin (V)')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('hanger_single_tone_PNA_3D_power_magramp_quick_scan.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

#variables

print 'Start Experiment'
#qt.msleep(5)

def display_time(time):
    hours = time/3600
    minutes = (time-3600*floor(hours))/60
    seconds = (time-3600*floor(hours)-60*floor(minutes))

    return hours, ':', minutes, ':', seconds
    


print 'Start sweeping'

def ramp_adwin_1(value):
    print 'ramp DAC 1 to ', value, '\n'
    adwin.set_DAC_1(value)
    while(True):
        actual_value=adwin.get_DAC_1()
        if(abs(value-actual_value)<0.01):
            return
        qt.msleep(.1)

IF=2

for magv in magvlist:
    print 'new frame magv', magv
    ramp_adwin_1(magv)

    IF=2
    new_outermostblockval_flag=True
    #adwin.set_DAC_1(gate)
   
    for power in power_list:

        
        IF=IF*2
            
        
        print 'frame ', magv, 'power ', power, ' IF ', IF
        pna.set_power(power)
        pna.set_resolution_bandwidth(IF)
        
        
        ave_list = np.linspace(1,averages,averages)
        #Set Voltage
        
        #print 'wait to settle'
        #
        qt.msleep(5)
        #qt.msleep(.2*sweeptime)
        
        #print 'sweep'
        pna.reset_averaging()
        for i in ave_list:
            pna.sweep()
            pna.auto_scale()

        trace=pna.fetch_data(polar=True)
        tr2=pna.data_f()

        data.add_data_point(flist, list(power*ones(len(flist))),list(magv*ones(len(flist))),trace[0], tr2, np.unwrap(trace[1]))

        data.new_block()
        spyview_process(data,start_freq,stop_freq,stop_power, start_power,magv,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
        
ramp_adwin_1(0)
data.close_file()
#adwin.set_DAC_1(0)

#adwin.set_DAC_1(0)
#adwin.set_DAC_2(0)

qt.mend()

#end of experiment routine

