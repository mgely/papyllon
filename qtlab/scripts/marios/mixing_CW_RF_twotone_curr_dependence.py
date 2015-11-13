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
execfile('setup_S21_twotone_XYZ.py')


################################
#      VARIABLES
################################


#maximum frequency in smb
fmax=20

#Core variables
X_name='Frequency [Hz]'
X_start=7.85e9#7.931e9-fmax*1e6-70e6
X_stop=7.95e9#7.931e9+fmax*1e6+10e6
X_points=1001
X_list=np.linspace(X_start,X_stop,X_points)

#27dB attenuation of cabling
#P_vna = 15 dBm

Y_name='RF freq [MHz]' 
Y_start=0.25
Y_stop=20
Y_points=80
Y_list=np.linspace(Y_start,Y_stop,Y_points)

Z_name='Current [A]'
Z_start=0#-28.5e-3
Z_stop=0#28.5e-3
Z_points=1#571
Z_list=np.linspace(Z_start,Z_stop,Z_points)



#For internal instrument variables see instruments section


#Core variables

# For the PNA (the number of points are set in the "setup_mixing.....py")

ifbw1=50           #of channel1 (sweep)
pow1=0

ifbw2=1e3           #of channel2 (CW)
pow2=-30

# For the FieldFox
ff_ifbw=500

# For the current source
v_max=200e-3

#source.set_output_type('CURR')
#source.set_voltage_protection(v_max)
#source.set_protection_state(True)



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

if 'ff' not in instlist:
    ff=visa.instrument('ff', 'FieldFox', address='TCPIP0::192.168.1.151::inst0::INSTR')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb', 'RS_SMB100A', address='TCPIP0::192.168.1.43::inst0::INSTR')



instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


timing.set_X_points(X_points)
timing.set_Y_points(Y_points)
timing.set_Z_points(Z_points)

timing.set_Y_name(Y_name)
timing.set_Z_name(Z_name)

##pna.reset()
##pna.setup(start_frequency=X_start,stop_frequency=X_stop,measurement_format = 'MLOG')
##pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
ff.set_mode('SA')
ff.set_start_frequency(X_start)
ff.set_stop_frequency(X_stop)
ff.set_resolution_bandwidth(ff_ifbw)
ff.set_sweeppoints(X_points)
#sweeptime = pna.get_sweeptime()*1.05


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
filename = 'mixing_CW_RF_twotone_curr_dependence'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate(X_name)
data.add_coordinate(Y_name)
data.add_coordinate(Z_name)
data.add_value('Spectrum (dBm)')
##data.add_value('f_data [dBm]')
##data.add_value('Phase unwrap')
##data.add_value('Phase raw')
##data.add_value('Voltage [V]')


data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('mixing_CW_RF_twotone_curr_dependence.py')


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



######################################
#       SETTING UP VNA DIRTY STYLE
######################################
pna.reset()
execfile('setup_mixing_CW_RF_curr_dependence.py')          #this uses std twotone script (channel 1 is doing a arbitrary sweep )
##pna.trigger(channel=1)
##pna.auto_scale()
pna_autoscale()
####source.set_bias_current(0)
####source.set_state(True)


pna.set_resolution_bandwidth(ifbw2,channel=2)

#let's measure the average of the noise floor
tr=0
pna.set_power_state('OFF',channel=1)
pna.w('SENS1:SWE:MODE SING')
tr_f=pna.data_f()
noise_f=array(tr).mean()
pna_autoscale()
pna.set_resolution_bandwidth(ifbw1,channel=1)

tr_polar=pna.fetch_data(polar=True)
noise_polar0=array(tr_polar[0]).mean()
noise_polar1=array(tr_polar[1]).mean()

pna.set_power_state('ON',channel=1)
pna.set_power(pow1,channel=1)
pna.set_power(pow2,channel=2)

ramp_source_curr(Z_list[0])
####qt.msleep(30)

for Z in Z_list:

    if (smb.get_RF_state()==False):
        smb.set_RF_state(True)

    if(source.get_state()==False):
        source.set_bias_current(0)
        source.set_state(True)
        
    timing.start_frame(Z_value=Z,publish=True)

    ramp_source_curr(Z)
    qt.msleep(1)
    voltage = source.get_measure_voltage()

    print 'voltage: \t' + str(voltage)
    
    new_outermostblockval_flag=True

    current_running=source.get_state()

    
    print 'current_running' + str(current_running)
    pna.w('SENS1:SWE:MODE SING')    #setup channel 1 to do a single sweep
    qt.msleep(bias_f_points/ifbw1)
    pna_autoscale()
    pna.peak_track(dip=False)   #get the peak
    peak=pna.get_peak()
    pna.w('SENS2:FREQ:CW %s' %(peak))   #do a CW on the peak
    
    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)

        

        if current_running==True:
            
            qt.msleep(0.01)
            smb.set_RF_frequency(Y)
            qt.msleep(0.01)

            ff.sweep()
            
            trace=ff.fetch_data()

            #now check if after our mw signal the current is still running

            curr_state = source.get_state()               

            print 'current running after sweep: \t' + str(curr_state)
            
            if(curr_state):

                
                voltage=source.get_measure_voltage()
                print 'current is still running, just save data and go to next power value'

                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),trace)
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.01) #wait 10 usec so save etc
            else:

                #hmm, current stopped, end powersweep
                voltage=0
                current_running=False

                print 'current stopped, fill the data with average_noise'
            
                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),list(noise_polar0*ones(len(X_list))),
                                    list(noise_f*ones(len(X_list))), list(noise_polar1*ones(len(X_list))),list(noise_polar1*ones(len(X_list))),
                                    list(voltage*ones(len(X_list))))
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.01) #wait 10 usec so save etc  

        else:
            
                #current_running became false, so we we fill the data of the rest of the power list with noise data

                data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),list(noise_polar0*ones(len(X_list))),
                                    list(noise_f*ones(len(X_list))), list(noise_polar1*ones(len(X_list))),list(noise_polar1*ones(len(X_list))),
                                    list(voltage*ones(len(X_list))))
                data.new_block()
                spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
                new_outermostblockval_flag=False
                qt.msleep(0.01) #wait 10 usec so save etc

data.close_file()
timing.stop(publish=True)

ramp_source_curr(0)
smb.set_RF_state(False)
qt.mend()

#end of experiment routine

