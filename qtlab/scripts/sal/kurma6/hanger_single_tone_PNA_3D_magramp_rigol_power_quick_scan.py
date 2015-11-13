################################
#       DESCRIBTION
################################

#Measurement script that does single tone qubit spectroscopy using the ADwin
#as a DAC to either sweep magnetic field of gate voltage.

def ramp_adwin_1(value,desired_rampspeed=.1):
    
    print 'ramp DAC 1 slowly to ', value, '\n'
    s1h_amplification_value = 3
    #with amp_value=3 & speed =0.1 ramping 15V takes 180s, thus about .1V/s so thats fine..
    #desired_rampspeed = .1 #V per sec
    
    current_value=adwin.get_DAC_1()
    delta = abs(value-current_value)
    required_time = delta/desired_rampspeed

    #print 'current_value ', current_value, ' delta ', delta, ' required_time ', required_time

    number_of_steps = required_time*50

    steplist = np.linspace(current_value,value, number_of_steps)

    now=time()
    for step in steplist:
        
        #print 'do step', step
        while(True):
        
            adwin.set_DAC_1(step)
            while(True):
                actual_value=adwin.get_DAC_1()
                if(abs(step-actual_value)<0.01):
                    break
                qt.msleep(.1)
            qt.msleep(0.02)
            break
    now2=time()
    print 'ramp duration ', now2-now

def ramp_rigol(value, desired_rampspeed=.05):
    #print 'ramp rigol to: ', value
    current_value = float(rigol.query("SOUR3:VOLT?"))
    delta = abs(value-current_value)
    required_time = delta/desired_rampspeed
    
    number_of_steps = required_time*10
    steplist=np.linspace(current_value,value,number_of_steps)
    #print steplist
    now=time()
    for step in steplist:
        rigol.write("SOUR3:VOLT %f" % step)
        qt.msleep(0.1)
        #print 'set to', step, 'after 10ms it is: ', rigol.query("SOUR3:VOLT?")
    qt.msleep(10)
    print 'ramp duration ', time()-now
            
    

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
f_points =601
bandwidth=100
power = 20
averages=1

h_1=4.44e9
h_2=5.176e9
h_3=6.2689e9
h_4=8.55e9

f_estimate=h_3
span=1200.e6

#start_freq=3.5e9
#stop_freq=9.5e9

start_freq=f_estimate-span/2
stop_freq=f_estimate+span/2

flist=np.linspace(float(start_freq),float(stop_freq),f_points)

start_power=15
stop_power=15

power_points=1

power_list=np.linspace(float(start_power),float(stop_power),power_points)


#1V=10mA
start_V=0
stop_V=5
#mag_d = 0.25
#magv_points = int((stop_magv - start_magv+1)/mag_d)

V_points = 201
V_list=np.linspace(float(start_V),float(stop_V),V_points)

iteration=np.linspace(1,1,3)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'timing' not in instlist:
    timing = qt.instruments.create('timing','timing')

if 'rigol' not in instlist:
    rigol = qt.instruments.create('rigol','universal_driver', address='TCIPIP::192.168.1.11::INSTR')

#if 'adwin_DAC' not in instlist:
#    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


timing.set_X_points(f_points)
timing.set_Y_points(V_points)
timing.set_Z_points(power_points)

timing.set_Y_name('magv')
timing.set_Z_name('power')

pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq,measurement_format = 'MLOG')
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
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
filename = 'hanger_single_tone_PNA_3D_magramp_rigol_power_quick_scan'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('V_rigol (10mA/V)')
data.add_coordinate('power (dBm)')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('hanger_single_tone_PNA_3D_magramp_rigol_power_quick_scan.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

#variables

#def ramp_adwin_1(value):
    #print 'ramp DAC 1 to ', value, '\n'
    #adwin.set_DAC_1(value)
   # while(True):
  #      actual_value=adwin.get_DAC_1()
 #       if(abs(value-actual_value)<0.01):
 #           return
#        qt.msleep(.1)

timing.start()

for power in power_list:

    timing.start_frame(Z_value=power,publish=True)
    pna.set_power(power)

    
    new_outermostblockval_flag=True
    #adwin.set_DAC_1(gate)
    #rigol.write("SOUR2:VOLT 0")
    #qt.msleep(30)
   
    for magv in V_list:
        timing.start_trace(Y_value=magv,Z_value=power,publish=True)
                
        
        
        ave_list = np.linspace(1,averages,averages)
        #Set Voltage
        ramp_rigol(magv)
        #rigol.write("SOUR2:VOLT %f" % magv)        #print 'wait to settle'
        #
        qt.msleep(10)
        #qt.msleep(.2*sweeptime)
        
        #print 'sweep'
        pna.reset_averaging()
        for i in ave_list:
            pna.sweep()
            pna.auto_scale()

        trace=pna.fetch_data(polar=True)
        tr2=pna.data_f()

        data.add_data_point(flist, list(magv*ones(len(flist))),list(power*ones(len(flist))),trace[0], tr2, np.unwrap(trace[1]))

        data.new_block()
        spyview_process(data,start_freq,stop_freq,stop_V, start_V,power,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
        

data.close_file()
timing.stop(publish=True)
ramp_rigol(0)

qt.mend()

#end of experiment routine

