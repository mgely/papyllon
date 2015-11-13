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
X_start=6.035e9
X_stop=6.135e9
X_points=51
X_list=np.linspace(X_start,X_stop,X_points)

Y_name='Current [A]'
Y_start=6900
Y_stop=7300
Y_points=101
Y_list=np.linspace(Y_start,Y_stop,Y_points)

Z_name='Power [dBm]'
Z_start=0
Z_stop=-10
Z_points=5
Z_list=np.linspace(Z_start,Z_stop,Z_points)



#For internal instrument variables see instruments section


#Core variables
power_cav=-15
ifbw=1e3

v_max=80e-3


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
pna.set_power(power_cav)
pna.set_resolution_bandwidth(ifbw)
pna.set_sweeppoints(X_points)
sweeptime = pna.get_sweeptime()*1.05


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
filename = 'S21_XYZ'
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
data.copy_file('S21_XYZ.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################


timing.start()

for Z in Z_list:

    timing.start_frame(Z_value=Z,publish=True)
    
    
    new_outermostblockval_flag=True
   
    for Y in Y_list:
        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)
           
        qt.msleep(0.01)

        pna.sweep()
        pna.auto_scale()

        trace=pna.fetch_data(polar=True)
        tr2=pna.data_f()

        data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),trace[0], tr2, np.unwrap(trace[1]))

        data.new_block()
        spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
        

data.close_file()
timing.stop(publish=True)

qt.mend()

#end of experiment routine

