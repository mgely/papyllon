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
X_start=7.84e9
X_stop=7.96e9
X_points=61
X_list=np.linspace(X_start,X_stop,X_points)

Y_name='Power [dB]'
Y_start=-15
Y_stop=8
Y_points=116
Y_list=np.linspace(Y_start,Y_stop,Y_points)

Z_name='Current [A]'
Z_start=-29.4e-3
Z_stop=29.4e-3
Z_points=295
Z_list=np.linspace(Z_start,Z_stop,Z_points)


#For internal instrument variables see instruments section

#Core variables
ifbw=100
v_max=200e-3


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

pna.reset()
pna.setup(start_frequency=X_start,stop_frequency=X_stop,measurement_format = 'MLOG')
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.set_resolution_bandwidth(ifbw)
pna.set_sweeppoints(X_points)
sweeptime = pna.get_sweeptime()*1.05


#let's measure the average off the noise floor

pna.set_power_state('OFF')
pna.sweep()
tr_f=pna.data_f()
noise_f=array(tr).mean()

tr_polar=pna.fetch_data(polar=True)
noise_polar0=array(tr_polar[0]).mean()
noise_polar1=array(tr_polar[1]).mean()

pna.set_power_state('AUTO')


#source settings
source.set_output_type('CURR')
source.set_voltage_protection(v_max)
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
filename = 'S21_fPI'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate(X_name)
data.add_coordinate(Y_name)
data.add_coordinate(Z_name)
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase unwrap')
data.add_value('Phase raw')
data.add_value('Voltage [V]')


data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('S21_fPI.py')


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

sou

for Z in Z_list:

    timing.start_frame(Z_value=Z,publish=True)

    if(source.get_state()==False):
        source.set_bias_current(0)
        source.set_state(True)

    
    ramp_source_curr(Z)
  
    voltage = source.get_measure_voltage()

    print 'voltage: \t' + str(voltage)
    
    new_outermostblockval_flag=True

    current_running=source.get_state()

    print 'current_running' + str(current_running)
       
    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)
        

        if current_running==True:
            

            pna.set_power(Y)
            qt.msleep(0.1)

            pna.sweep()
            pna.auto_scale()
            

            trace=pna.fetch_data(polar=True)
            tr2=pna.data_f()


            #now check if after our mw signal the current is still running

            curr_state = source.get_state()

            
            print 'current running after sweep: \t' + str(curr_state)
            ############### this is to fill with noise the birfucated data due to high power (bad programming!!!!)
            pna.peak_track(dip=False)
            ypeak=pna.q('CALC:MARK:Y?')
            if(curr_state) and ypeak[0]=='+':
            ###############

                
                voltage=source.get_measure_voltage()
                print 'current is still running, just save data and go to next power value'

                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),trace[0], tr2, np.unwrap(trace[1]),trace[1],list(voltage*ones(len(X_list))))
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.01) #wait 10 usec so save etc

                
            
   
            else:

                #hmm, current stopped, end powersweep
                voltage=0
                current_running=False

                print 'current stopped (or high power), fill the data with average_noise'
            
                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),list(noise_polar0*ones(len(X_list))),
                                    list(noise_f*ones(len(X_list))), list(noise_polar1*ones(len(X_list))),list(noise_polar1*ones(len(X_list))),
                                    list(voltage*ones(len(X_list))))
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.01) #wait 10 usec so save etc
                qt.msleep(1) 
                
        else:
                #current_running became false, so we we fill the data of the rest of the power list with noise data

                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),list(noise_polar0*ones(len(X_list))),
                                    list(noise_f*ones(len(X_list))), list(noise_polar1*ones(len(X_list))),list(noise_polar1*ones(len(X_list))),
                                    list(voltage*ones(len(X_list))))
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.1) #wait 10 usec so save etc
        

data.close_file()
timing.stop(publish=True)

qt.mend()
ramp_source_curr(0)
#end of experiment routine

