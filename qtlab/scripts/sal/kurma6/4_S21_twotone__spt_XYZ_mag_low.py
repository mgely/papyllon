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



################################
#      VARIABLES
################################


#Cavity monitor
bias_start_cav = 4.5e9
bias_stop_cav = 5.5e9
bias_f_points =601
bias_ifbw = 50
bias_pow=0
bias_aver_cav=1
aver_cav=1
w_bare=4.609e9
bias_aver_cav_list=np.linspace(1,1,aver_cav)

execfile('setup_S21_twotone_XYZ.py')

#Core variables
X_name='Probe Frequency [Hz]'
X_start=0.01e9
X_stop=4e9
X_points=1001
X_list=np.linspace(X_start,X_stop,X_points)


X_name_cav='Cavity Frequency [Hz]'
X_start_cav = 4.5e9
X_stop_cav= 5.5e9
X_points_cav= 601
X_list_cav=np.linspace(X_start_cav,X_stop_cav,X_points_cav)


Y_name='I coil [mA]'
#Y_name='V coil [V]'
Y_start=-0.15
Y_stop=0.08
Y_points=101
Y_list=np.linspace(Y_start,Y_stop,Y_points)

##Y_name='Probe power [dBm]'
###Y_name='V coil [V]'
##Y_start=30
##Y_stop=15
##Y_points=6
##Y_list=np.linspace(Y_start,Y_stop,Y_points)

Z_name='Probe power [dBm]'
#Y_name='V coil [V]'
Z_start=27
Z_stop=15
Z_points=5
Z_list=np.linspace(Y_start,Y_stop,Y_points)


    

#var_att=80dB
##
##Z_name='Cavity power [dBm]'
##Z_start=-10
##Z_stop=-21
##Z_points=8
##Z_list=np.linspace(Z_start,Z_stop,Z_points)


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

base_path = 'D:\\data\\Sal\\KURMA6A_10mK\\'

now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)




#Set up data
filename = 'S21_twotone_XYZ_mag_low'
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
data.copy_file('4_S21_twotone__spt_XYZ_mag_low.py')
data.copy_file('setup_S21_twotone_XYZ.py')

#Set up data cavity tone
filename_cav = 'S21_twotone_XYZ_cav'
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
pow_cav = -12
aver_probe=8
ifbw_probe=50
aver_list=np.linspace(1,1,aver_probe)


pna_set_2tone_probe_frequency(start_frequency=X_start,stop_frequency=X_stop, points=X_points,ifbw=ifbw_probe)
pna.w("SENS2:AVER:COUN %s" % (aver_probe))

timing.start()
pna_set_2tone_probe_power(15)

#set cavity power

pna.w("SOUR2:POW1 %s" %(pow_cav))    

def reset_cav():
    pna_set_2tone_cw_f(measure_cav())
    

for Z in Z_list:
    timing.start_frame(Z_value=Z,publish=True)
    
    #adwin.set_sec_DAC_1(Z)
    #qt.msleep(4)
    
    new_outermostblockval_flag=True

    #set cavity power
#    pna.w("SOUR2:POW1 %s" %(Z))
    #set probe power
    pna_set_2tone_probe_power(Z)
    #aver_probe=aver_probe/2.    
    aver_list=np.linspace(1,1,aver_probe)
    
    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)
        
        #set magnet
        curr_source.set_bias_current(Y*1e-3)

        #pna.w("SOUR2:POW1 %s" %(Y))    

        qt.msleep(1)
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
       
        
curr_source.set_bias_current(0)
curr_source.set_state(False)

data.close_file()
timing.stop(publish=True)


qt.mend()

#end of experiment routine

