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

#For internal instrument variables see instruments section


#Core variables
f_points =20001
bandwidth=100
power = 30
averages=1

#h_1=4.44e9
#h_2=5.176e9
#h_3=6.2689e9
#h_4=8.55e9

#f_estimate=h_3
#span=1000.e6

start_freq=2e9
stop_freq=16e9

#start_freq=f_estimate-span/2
#stop_freq=f_estimate+span/2

flist=np.linspace(float(start_freq),float(stop_freq),f_points)


start_Y=1
stop_Y=4001
Y_points=4000


Ylist=np.linspace(float(start_Y),float(stop_Y),Y_points)

start_Z=1
stop_Z=1
Z_points=1
Zlist=np.linspace(float(start_Z),float(stop_Z),Z_points)

#iteration=np.linspace(1,1,3)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#if 'pna' not in instlist:
#    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'adwin' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC_sal_inout',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)



pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq,measurement_format = 'MLOG')
pna.set_power(power)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
pna.set_averages_on()
pna.set_averages(averages)
sweeptime = pna.get_sweeptime()*1.05

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program
#adwin.set_rampsteps(100)
#adwin.set_DAC_1(0)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Sal\\Split_cav_KIT\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed



#Set up data
filename = 'S21'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('Y')
data.add_coordinate('Z')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('S21.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

#variables

print 'Start Experiment'
#qt.msleep(5)



print 'Start sweeping'

def ramp_adwin_1(value):
    print 'ramp DAC 1 to ', value, '\n'
    adwin.set_DAC_1(value)
    while(True):
        actual_value=adwin.get_DAC_1()
        if(abs(value-actual_value)<0.01):
            return
        qt.msleep(.1)

def ramp_adwin_2(value):
    print 'ramp DAC 2 to ', value, '\n'
    adwin.set_DAC_2(value)
    while(True):
        actual_value=adwin.get_DAC_2()
        if(abs(value-actual_value)<0.01):
            return
        qt.msleep(.1)

for Z in Zlist:
    print 'new Z-frame with value ' , Z

    #set your Z-coordinate
    #ramp_adwin_1(magv)
    qt.msleep(.5)
    
    new_outermostblockval_flag=True
    
   
    for Y in Ylist:
        print 'Y ', Y, 'Z ', Z
        
        
        
        ave_list = np.linspace(1,averages,averages)

        #Set your Y-coordinate
        #ramp_adwin_2(gate)
        #print 'wait to settle'
        #
        #ramp_adwin_1(Y)
        
        qt.msleep(.5)
        #qt.msleep(.2*sweeptime)
        
        #print 'sweep'
        pna.reset_averaging()
        for i in ave_list:
            pna.sweep()
            qt.msleep(0.1)
            pna.auto_scale()
            qt.msleep(0.1)

        trace=pna.fetch_data(polar=True)
        qt.msleep(0.5)
        tr2=pna.data_f()
        qt.msleep(0.5)
        data.add_data_point(flist, list(Y*ones(len(flist))),list(Z*ones(len(flist))),trace[0], tr2, np.unwrap(trace[1]))

        data.new_block()
        spyview_process(data,start_freq,stop_freq,stop_Y, start_Y,Z,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
        qt.msleep(120)
        

data.close_file()
#adwin.set_DAC_1(0)

#adwin.set_DAC_1(0)
#adwin.set_DAC_2(0)

qt.mend()

#end of experiment routine
