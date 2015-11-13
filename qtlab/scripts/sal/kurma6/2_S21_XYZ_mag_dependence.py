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




#Core variables
X_name='Cavity Frequency [Hz]'
X_start=3.90e9
X_stop=5.3e9
X_points=2801
X_list=np.linspace(X_start,X_stop,X_points)

Y_name='I_coil [A]'
Y_start=-2.e-3
Y_stop=2.e-3
Y_points=3201
Y_list=np.linspace(Y_start,Y_stop,Y_points)

Z_name='var_att [dB]'
Z_start=80
Z_stop=80
Z_points=1
Z_list=np.linspace(Z_start,Z_stop,Z_points)



#For internal instrument variables see instruments section


#Core variables
power_pna=0
ifbw=50
averages=1

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

if 'curr_source' not in instlist:
    curr_source = qt.instruments.create('curr_source', 'keysight_source_B2961A', address='TCPIP::192.168.1.56::INSTR')


if 'var_att' not in instlist:
    var_att=qt.instruments.create('var_att','agilent_var_att', address='TCPIP::192.168.1.113::INSTR')


instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


timing.set_X_points(X_points)
timing.set_Y_points(Y_points)
timing.set_Z_points(Z_points)

timing.set_Y_name(Y_name)
timing.set_Z_name(Z_name)

pna.reset()
pna.setup(start_frequency=X_start,stop_frequency=X_stop,measurement_format = 'MLOG')
#pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.set_power(power_pna)
pna.set_resolution_bandwidth(ifbw)
pna.set_sweeppoints(X_points)
pna.set_averages_on()
pna.set_averages(averages)
sweeptime = pna.get_sweeptime()*1.05

curr_source.set_output_type('CURR')
curr_source.set_voltage_protection(0.1)
curr_source.set_protection_state(True)
curr_source.set_state(True)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Sal\\KURMA6A_10mK\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed



#Set up data
filename = 'S21_XYZ_mag_dependence'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate(X_name)
data.add_coordinate(Y_name)
data.add_coordinate(Z_name)
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('2_S21_XYZ_mag_dependence.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################


timing.start()

for Z in Z_list:

    timing.start_frame(Z_value=Z,publish=True)
    
    var_att.set_var_att(Z)
    
    new_outermostblockval_flag=True
   
    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)

        curr_source.set_bias_current(Y)
        
           
        ave_list = np.linspace(1,averages,averages)
        qt.msleep(0.01)
        #print 'sweep'
        pna.reset_averaging()
        for i in ave_list:
            pna.sweep()
            pna.auto_scale()

        trace=pna.fetch_data(polar=True)
        tr2=pna.data_f()

        data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),trace[0], tr2, np.unwrap(trace[1]))

        data.new_block()
        spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
curr_source.set_bias_current(0.0)
curr_source.set_state(False)       

data.close_file()
timing.stop(publish=True)

qt.mend()

#end of experiment routine

