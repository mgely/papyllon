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


#Core variables
X_name='Frequency [MHz]'
X_start=-10
X_stop=10
X_points=21
X_list=np.linspace(X_start,X_stop,X_points)

Y_name='Current [mA]'
Y_start=-10
Y_stop=10
Y_points=21
Y_list=np.linspace(Y_start,Y_stop,Y_points)

Z_name='Voltage [V]'
Z_start=-10
Z_stop=10
Z_points=201
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

base_path = 'D:\\data\\Sal\\QTlab_dev\\'

now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)




#Set up data
filename = 'XYZ'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('X')
data.add_coordinate('Y')
data.add_coordinate('Z')
data.add_value('measurement_output')
data.add_value('elapsed_time[s]')
data.add_value('interval[s]')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('XYZ.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################


timing.start()

for Z in Z_list:
    

    qt.msleep(.5)
    
    new_outermostblockval_flag=True

    timing.start_frame(Z_value=Z,publish=True)
    
    
    for Y in Y_list:
        
        my_data = []
        elapsed_time = []
        interval=[]

        timing.start_trace(Y_value=Y,Z_value=Z,publish=True)
        
        for X in X_list:

            my_data.append(0)
            elapsed_time.append(timing.get_elapsed_time())
            interval.append(timing.interval())
            
            qt.msleep(.01*np.random.random())
            

        data.add_data_point(X_list, list(Y*ones(len(X_list))),list(Z*ones(len(X_list))),my_data,elapsed_time,interval)
        data.new_block()
        spyview_process(data,X_start,X_stop,Y_stop, Y_start,Z,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
        

data.close_file()
timing.stop(publish=True)


qt.mend()

#end of experiment routine

