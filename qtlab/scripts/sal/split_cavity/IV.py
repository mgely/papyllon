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

#uA = 1e-3

#Core variables
start_I = -1
stop_I = 1

I_points=100


Ilist=np.linspace(float(start_I),float(stop_I),I_points)


    


iteration1=np.linspace(1,1,10)
iteration2=np.linspace(1,1,10)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#if 'adwin_DAC' not in instlist:
#    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#adwin_DAC initialization
#adwin.start_process()       #starts the DAC program
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
filename = 'IV'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Bias current (nA)')
data.add_coordinate('iteration1')
data.add_coordinate('iteration2')
data.add_value('Voltage (uV)')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('IV.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

#variables

print 'Start Experiment'
#qt.msleep(5)






def ramp_adwin_1(value):
    print 'ramp DAC 1 to ', value, '\n'
    adwin.set_DAC_1(value)
    while(True):
        actual_value=adwin.get_DAC_1()
        if(abs(value-actual_value)<0.01):
            return
        qt.msleep(.01)

def ramp_adwin_2(value):
    print 'ramp DAC 2 to ', value, '\n'
    adwin.set_DAC_2(value)
    while(True):
        actual_value=adwin.get_DAC_2()
        if(abs(value-actual_value)<0.01):
            return
        qt.msleep(.01)


for ite1 in iteration1:
    print 'new iteration1 z-axis' , ite1

    qt.msleep(.5)
    
    new_outermostblockval_flag=True

    for ite2 in iteration2:
        print 'new iteration2 y-axis', ite2
        Vlist = []
        for I in Ilist:
            
        
        
            ramp_adwin_1(I)
            qt.msleep(.001)
            vread = adwin.get_ADC_1()
            print 'bias current ', I, 'read voltage ', vread
            Vlist.append(vread)

        data.add_data_point(Ilist, list(ite2*ones(len(Ilist))),list(ite1*ones(len(Ilist))),Vlist)
        Vlist=[]
        data.new_block()
        spyview_process(data,start_I,stop_I,10, 1,ite1,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
       
        

data.close_file()
#adwin.set_DAC_1(0)

#adwin.set_DAC_1(0)
#adwin.set_DAC_2(0)

qt.mend()

#end of experiment routine

