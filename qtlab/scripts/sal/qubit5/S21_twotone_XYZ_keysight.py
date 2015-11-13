################################
#       DESCRIBTION
################################

#Template script for 3D-measurment including timing




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

execfile('setup_S21_twotone_XYZ.py')

################################
#      VARIABLES
################################

def ramp_source(value,desired_rampspeed=.001):
    
    print 'ramp source 1 slowly to ', value, '\n'
    s1h_amplification_value = 3
    #with amp_value=3 & speed =0.1 ramping 15V takes 180s, thus about .1V/s so thats fine..
    #desired_rampspeed = .1 #V per sec
    
    current_value=source.get_bias_current()
    delta = abs(value-current_value)
    required_time = delta/desired_rampspeed

    #print 'current_value ', current_value, ' delta ', delta, ' required_time ', required_time

    number_of_steps = required_time*50

    steplist = np.linspace(current_value,value, number_of_steps)

    now=time()
    for step in steplist:
        
        #print 'do step', step
        while(True):
        
            source.set_bias_current(step)
            qt.msleep(.2)
            while(True):
                actual_value=source.get_bias_current()
                if(abs(step-actual_value)<0.0001):
                    break
                qt.msleep(1)
            qt.msleep(0.02)
            break
    now2=time()
    print 'ramp duration ', now2-now






#Core variables
X_name='Probe Frequency [Hz]'
X_start=3.0e9
X_stop=6.0e9
X_points=1501
X_list=np.linspace(X_start,X_stop,X_points)


X_name_cav='Cavity Frequency [Hz]'
X_start_cav = 6.035e9
X_stop_cav= 6.135e9
X_points_cav= 201
X_list_cav=np.linspace(X_start_cav,X_stop_cav,X_points_cav)

mA=1e-3
#Y_name='Probe power [dBm]'
Y_name='V coil [V]'
Y_start=-60*mA
Y_stop=-65*mA
Y_points=51
Y_list=np.linspace(Y_start,Y_stop,Y_points)
    



Z_name='Cavity power [dBm]'
Z_start=-15
Z_stop=0
Z_points=3
Z_list=np.linspace(Z_start,Z_stop,Z_points)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'timing' not in instlist:
    timing = qt.instruments.create('timing','timing')

timing.set_X_points(X_points)
timing.set_Y_points(Y_points)
timing.set_Z_points(Z_points)

timing.set_Y_name(Y_name)
timing.set_Z_name(Z_name)



#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Sal\\LETO11V_twotone\\'

now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)




#Set up data
filename = 'S21_twotone_XYZ_keysight'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate(X_name)
data.add_coordinate(Y_name)
data.add_coordinate(Z_name)
data.add_value('Raw power [dBm]')
data.add_value('Amplitude [dBm]')
data.add_value('Phase [dBm]')
data.add_value('f_cav [Hz]')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('S21_twotone_XYZ_keysight.py')
data.copy_file('setup_S21_twotone_XYZ.py')

#Set up data cavity tone
filename_cav = 'S21_twotone_XYZ_cav_keysight'
data_cav = qt.Data(name=filename_cav)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data_cav.add_coordinate(X_name)
data_cav.add_coordinate(Y_name)
data_cav.add_coordinate(Z_name)
data_cav.add_value('Amplitude [dBm]')
data_cav.add_value('Phase [dBm]')
data_cav.add_value('f_cav [Hz]')

data_cav.create_file(datadirs=base_path+date_path+'_____'+filename_cav)




spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

#pna_set_2tone_cw_power(-6)

aver_probe=10
ifbw_probe=1000
aver_list=np.linspace(1,1,aver_probe)


pna_set_2tone_probe_frequency(start_frequency=X_start,stop_frequency=X_stop, points=X_points,ifbw=ifbw_probe)
pna.w("SENS2:AVER:COUN %s" % (aver_probe))

timing.start()
pna_set_2tone_probe_power(20)
for Z in Z_list:
    timing.start_frame(Z_value=Z,publish=True)
    
    #adwin.set_sec_DAC_1(Z)
    #qt.msleep(4)
    
    new_outermostblockval_flag=True

    #set cavity power
    pna.w("SOUR2:POW1 %s" %(Z))    
    #aver_probe=aver_probe/2.    
    aver_list=np.linspace(1,1,aver_probe)
    
    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)
        #pna_set_2tone_probe_power(Y)
        ramp_source(Y)
        #track cavity
        f_cav = measure_cav()
        pna_autoscale()
        pna_set_2tone_cw_f(f_cav)

        print 'measured f_cav' , f_cav

        for i in aver_list:
            #print 'aver', i
            pna.trigger(channel=2)
            pna_autoscale()

        s21 = pna.fetch_data(channel=2,polar=True)
        formatted_data=pna.fetch_formatted_data(channel=2)

        data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),formatted_data,s21[0],s21[1],list(f_cav*ones(len(X_list))))
        data.new_block()
        spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
        

data.close_file()
timing.stop(publish=True)


qt.mend()

#end of experiment routine

