################################
#      IMPORTS
################################

import qt
import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime

#execfile('metagen.py')

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'rigol' not in instlist:
    rigol= qt.instruments.create('rigol','rigol_dm3058',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')

if 'keithley' not in instlist:
    keithley= qt.instruments.create('keithley','Keithley_2700',address='GPIB0::17::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#measurement information stored in manual in MED instrument
med.set_device('R-T of MoRe two probe device')
med.set_setup('DC poorman with T sensor')
med.set_user('Vibhor')

print rigol.query('*IDN?')

#Set up both DMM



################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()

#Set up data
filename = 'R-T data'
data = qt.Data(name=filename)
data.add_coordinate('time [s]')
data.add_value('Temp[K]')
data.add_value('4p-Resistance[Ohm]')


base_path = 'D:\\data\\Vibhor\\RT_anneal_sample\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)

data.copy_file('R_T_v02.py')

plot1=qt.Plot2D(data, name='T [K]', coorddim=0, valdim=1)
plot2=qt.Plot2D(data, name='R [Ohm]', coorddim=0, valdim=2)


# VARIABLES

max_runtime = 100000;

###############################
# Measurement loop

tstart = time()
x_time = 0
y_temp =0

while (x_time < max_runtime):
    
    x_time = time()- tstart
    #y_temp = float(rigol.value()[13:])
    y_temp = (float(rigol.value()[13:])-221.7)*(300-4.2)/(291-221.7)+4.2
    #temperature converted to [K] (calibration by Vibhor)
    keithley.set_mode_res()
    keithley.set_autorange(True)
    keithley.set_trigger_disc()
    Resis=keithley.get_readval()
    data.add_data_point(x_time,y_temp,Resis) #store data
    print y_temp, Resis
    qt.msleep(2) #  wait 1 sec so save etc

data.close_file()
qt.mend()
#end
