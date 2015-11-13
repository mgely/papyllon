################################
#       DESCRIPTION
################################

#


################################
#       DEVELOPMENT NOTES/LOG
################################



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




#Core variables
X_name='Frequency [Hz]'
X_start=7.75e9
X_stop=8.05e9
X_points=301
X_list=np.linspace(X_start,X_stop,X_points)

Y_name='Voltage [V]'
Y_start=0#-100e-3
Y_stop=100e-3
Y_points=51
Y_list=np.linspace(Y_start,Y_stop,Y_points)


Z_name='Power [dB]'
Z_start=-30
Z_stop=10
Z_points=5#7
Z_list=np.linspace(Z_start,Z_stop,Z_points)

var_att.set_var_att(0)
#For internal instrument variables see instruments section

#Core variables
ifbw=1e3
i_max=40e-3

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A_sal', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'timing' not in instlist:
    timing = qt.instruments.create('timing','timing')

if 'source' not in instlist:
    source = qt.instruments.create('source', 'keysight_source_B2961A', address='TCPIP::192.168.1.56')




instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


timing.set_X_points(X_points)
timing.set_Y_points(Y_points)
timing.set_Z_points(Z_points)

timing.set_Y_name(Y_name)
timing.set_Z_name(Z_name)

######################################
#       SETTING UP VNA DIRTY STYLE
######################################
pna.reset()
execfile('setup_mixing_CW_RF_curr_dependence.py')          #this uses std twotone script (channel 1 is doing a arbitrary sweep )
pna_autoscale()

##pna.setup(start_frequency=X_start,stop_frequency=X_stop,measurement_format = 'MLOG')
##pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
##pna.set_resolution_bandwidth(ifbw,channel=1)
pna.set_sweeppoints(X_points)
sweeptime = pna.get_sweeptime()*1.05

pna.w("SENS:FREQ:START %s" % (X_start))
pna.w("SENS:FREQ:STOP %s" % (X_stop))
pna.w("SENS:SWE:POIN %s" % (X_points))

#let's measure the average off the noise floor

tr=0
pna.set_power_state('OFF',channel=1)
pna.w('SENS1:SWE:MODE SING')
tr_f=pna.data_f()
noise_f=array(tr).mean()
pna_autoscale()
pna.set_resolution_bandwidth(ifbw,channel=1)
pna.set_resolution_bandwidth(ifbw,channel=2)

tr_polar=pna.fetch_data(polar=True)
noise_polar0=array(tr_polar[0]).mean()
noise_polar1=array(tr_polar[1]).mean()

pna.set_power_state('ON',channel=1)
pna.set_power(Y,channel=1)
pna.set_power(Y,channel=2)

#source settings
source.set_output_type('VOLT')
source.set_current_protection(i_max)
source.set_protection_state(True)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Marios\\Phoebe1_4K\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed



#Set up data
filename = 'IVcurve-CWtone'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate(X_name)
data.add_coordinate(Y_name)
data.add_coordinate(Z_name)
data.add_value('Current [A]')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase unwrap')
data.add_value('Phase raw')



data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('IVcurve-CWtone.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################



def ramp_source_curr(value, wait=10e-3, step_size=1e-4):
    print 'ramp source to ', value, '\n'
    
    ramp_d = value-source.get_bias_current() 
    ramp_sign = np.sign(ramp_d)

    ramp_bool = True
    while(ramp_bool):
        actual_value=source.get_bias_current()
        if(abs(value-actual_value)<2*step_size):
            source.set_bias_current(value)
            ramp_bool = False
        else:
            source.set_bias_current(actual_value+ramp_sign*step_size)
            qt.msleep(wait)
    return value


timing.start()

source.set_bias_voltage(Y_list[0])

for Z in Z_list:
    timing.start_frame(Z_value=Z,publish=True)
    
    pna.set_power(Z,channel=1)
    pna.w('SENS1:SWE:MODE SING')    #setup channel 1 to do a single sweep

    pna_autoscale()
    pna.peak_track(dip=False)   #get the peak
    peak=pna.get_peak()
    qt.msleep(1)
    pna.set_power(Z,channel=2)
    pna.w('SENS2:FREQ:CW %s' %(peak))   #do a CW on the peak
    pna_autoscale()
    
    new_outermostblockval_flag=True

    

    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)
        
        current_running=source.get_state()
        if(source.get_state()==False):
            #source.set_bias_current(0)
            source.set_state(True)

        print 'current_running' + str(current_running)
        if current_running==True:
            
            source.set_bias_voltage(Y)
    

    

            qt.msleep(0.01)

            trace=pna.fetch_data(polar=True)
            tr2=pna.data_f()
            
            current = source.get_measure_current()

            print 'current: \t' + str(current)

            #now check if the current is still running

            curr_state = source.get_state()

            
            print 'current running after sweep: \t' + str(curr_state)

            if(curr_state):

                
                current = source.get_measure_current()
                print 'current is still running, just save data and go to next power value'

                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),list(current*ones(len(X_list))),trace[0], tr2, np.unwrap(trace[1]),trace[1])
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.01) #wait 10 usec so save etc

                
            
   
            else:

                #hmm, current stopped, end powersweep
                current=0
                current_running=False

                print 'current stopped (or high power), fill the data with average_noise'
            
                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),
                                    list(current*ones(len(X_list))),list(noise_polar0*ones(len(X_list))),
                                    list(noise_f*ones(len(X_list))), list(noise_polar1*ones(len(X_list))),list(noise_polar1*ones(len(X_list))))
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.01) #wait 10 usec so save etc
                #qt.msleep(1) 
                
        else:
                #current_running became false, so we we fill the data of the rest of the power list with noise data

                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),
                                    list(current*ones(len(X_list))),list(noise_polar0*ones(len(X_list))),
                                    list(noise_f*ones(len(X_list))), list(noise_polar1*ones(len(X_list))),list(noise_polar1*ones(len(X_list))))
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.1) #wait 10 usec so save etc
        

data.close_file()
timing.stop(publish=True)

qt.mend()
pna.set_power_state('OFF',channel=1)
pna.set_power_state('OFF',channel=2)
pna.sweep()
source.set_state(False)
source.set_bias_voltage(0)
#end of experiment routine

