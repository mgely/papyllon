################################
#      IMPORTS
################################

import qt
import numpy as np
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute, ones
from time import time, sleep, localtime, strftime
#execfile('metagen2D.py')
execfile('metagen3D.py')



################################
#      VARIABLES
################################

# var_att is 80dB
# probe attenuation is 20dB
#Cavity monitor
bias_start_cav = 4.1e9
bias_stop_cav = 4.5e9
bias_f_points =20
bias_ifbw = 20
bias_pow=-9
bias_aver_cav=1 # NOT IMPLEMENTED
aver_cav=1
w_bare=4.601e9
bias_aver_cav_list=np.linspace(1,1,aver_cav) # NOT IMPLEMENTED

execfile('setup_S21_twotone_XYZ.py')

#Core variables
X_name='Probe Frequency [Hz]'
X_start=7.0e9
X_stop=15.e9
X_points=100
X_list=np.linspace(X_start,X_stop,X_points)


X_name_cav='Cavity Frequency [Hz]'
X_start_cav = 4.6e9
X_stop_cav= 4.7e9
X_points_cav= 20
X_list_cav=np.linspace(X_start_cav,X_stop_cav,X_points_cav)


Y_name='I coil [mA]'
Y_start=0.5
Y_stop=1.7
Y_points=501
Y_list=np.linspace(Y_start,Y_stop,Y_points)

# Y_name='Probe power [dBm]'
# Y_start=-6.
# Y_stop=6.
# Y_points=5
# Y_list=np.linspace(Y_start,Y_stop,Y_points)

# The probe power is 
Z_name='Probe power defined from detuning'
Z_start=0.
Z_stop=0.
Z_points=1
Z_list=np.linspace(Z_start,Z_stop,Z_points)


    

#var_att=80dB
##
# Z_name='Cavity power [dBm]'
# Z_start=-18.
# Z_stop=-12.
# Z_points=3
# Z_list=np.linspace(Z_start,Z_stop,Z_points)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

timing = qt.instruments.create('timing','timing')
var_att = qt.instruments.create('var_att','agilent_var_attenuator',address='TCPIP::192.168.1.113::INSTR')
curr_source = qt.instruments.create('curr_source', 'keysight_source_B2961A', address='TCPIP::192.168.1.56::INSTR')
curr_source.set_output_type('CURR')
curr_source.set_state(True)

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
filename = 'S21_twotone_XYZ_mag_high'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate(X_name)
data.add_coordinate(Y_name)
data.add_coordinate(Z_name)
data.add_value('linmag')
data.add_value('Phase [dBm]')
data.add_value('f_cav [Hz]')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('6_S21_twotone__spt_XYZ_mag_high.py')
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

data_cav.create_file(datadirs=base_path+date_path+'_____'+filename_cav) # NOT IMPLEMENTED




spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

def qubit_frequency_for_current(I):
    f0 = 10.5e9
    alpha = 6.41e9
    I0 = 1.125 #mA
    return f0-alpha*(I-I0)**2.

# Since the frequency of the qubit oscillations induced by the cavity drive is linearly related to the detuning
# we be changing the probe power linearly as a function of the detuning, in order to achieve a constant qubit line-width (hopefully)
# At the lowest frequency point, I=0.5mA, fq = 8GHz, and we get a minimal bandwidth (without impacting the amplitude of the peak) by
# setting the probe power to -25 dBm. For the sweet spot, I=1.125mA, fq = 10.45GHz, we set -9 dBm.
def set_probe_power(I):
    f_q = qubit_frequency_for_current(I)
    f_ssp = qubit_frequency_for_current(1.125)
    P_ssp = -9.

    f_vrsp = qubit_frequency_for_current(0.5)
    P_vrsp = -25.

    P = P_ssp + (P_vrsp-P_ssp)*(f_q-f_ssp)/(f_vrsp-f_ssp)
    return P


#pna_set_2tone_cw_power(-6)
pow_cav = -18.
aver_probe=8
ifbw_probe=50
aver_probe=1
aver_list=np.linspace(1,1,aver_probe)


pna_set_2tone_probe_frequency(start_frequency=X_start,stop_frequency=X_stop, points=X_points,ifbw=ifbw_probe)
pna.w("SENS2:AVER:COUN %s" % (aver_probe))

timing.start()
pna_set_2tone_probe_power(0)

#set cavity power

pna.w("SOUR2:POW1 %s" %(10))    # WTF?

var_att.set_var_att(80)

def reset_cav():
    pna_set_2tone_cw_f(measure_cav())
    

for Z in Z_list:
    timing.start_frame(Z_value=Z,publish=True)
    
    #adwin.set_sec_DAC_1(Z)
    #qt.msleep(4)
    
    new_outermostblockval_flag=True

    #set cavity power
#    pna.w("SOUR2:POW1 %s" %(Z))


    #aver_probe=aver_probe/2.    
    aver_list=np.linspace(1,1,aver_probe)
    
    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)
        
        #set magnet
        curr_source.ramp_source_curr(Y*1e-3,10e-3,1e-6)
        #set probe power
        probe_att = set_probe_power(Y)
        print "probe attenuation set to: ", probe_att
        pna_set_2tone_probe_power(probe_att)

        # pna.w("SOUR2:POW1 %s" %(Y))    

        qt.msleep(1)
        #track cavity

        ############### reset cavity and autoscale
        f_cav = measure_cav()
        pna_autoscale()
        pna_set_2tone_cw_f(f_cav)

        print 'measured f_cav' , f_cav

        for i in aver_list:
            #print 'aver', i
            pna.trigger(channel=2)
            pna_autoscale()

        trace = pna.fetch_data(channel=2,polar=True)
        # formatted_data=pna.fetch_formatted_data(channel=2)

        data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),trace[0], np.unwrap(trace[1]),list(f_cav*ones(len(X_list))))
        data.new_block()
        spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
        
# curr_source.set_bias_current(0)
curr_source.ramp_source_curr(0.,10e-3,1e-6)
source.set_state(False)

data.close_file()
timing.stop(publish=True)


qt.mend()

#end of experiment routine

