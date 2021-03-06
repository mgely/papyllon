################################
#       DESCRIBTION
################################

#Script that measures the frequency response of a MW hanger and finds the Qc, Qi, fres
#it works as follows:

#you enter a scan_range, span
#first the PNA does a quick scan to find the resonance approximately
#then in a second scan the resonance is detailed measured and fitted




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


from pylab import *
from scipy import *
from scipy import optimize
 

################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec



f_points =2001
bandwidth=100
power = -5
averages=1

h_1=4.46e9
h_2=5.17e9
h_3=6.38e9
h_4=7.81e9

f_estimate=h_4
span=500.e6

start_f=f_estimate-span/2.
stop_f=f_estimate+span/2.

f_list=np.linspace(start_f,stop_f,f_points)

iteration=1
iteration_list=np.linspace(1,1,iteration)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


pna.reset()
pna.setup(start_frequency=start_f,stop_frequency=stop_f,measurement_format = 'MLOG')
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.set_power(power)
pna.set_averages(True)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

device_name = 'LETO11V_10mK'

base_path = 'D:\\data\\Sal\\' + device_name + '\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed

#Set up data
filename = 'hanger_characterization'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('iteration1')
data.add_coordinate('iteration2')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('hanger_characterization.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

print 'Start Experiment'

  
for i in iteration_list:
    
    new_outermostblockval_flag=True
    #adwin.set_DAC_1(gate)
   
    for j in iteration_list:
        #print magv
        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time

        
        ave_list = np.linspace(1,averages,averages)
        #Set Voltage
        #adwin.set_DAC_2(magv)
        #print 'wait to settle'
        #
        qt.msleep(.2)
        #qt.msleep(.2*sweeptime)
        
        #print 'sweep'
        pna.reset_averaging()
        for k in ave_list:
            pna.sweep()
            pna.auto_scale()

        trace=pna.fetch_data(polar=True)
       
        tr2=pna.data_f()
        
        #tr2_parsed = pna.parse_trace(tr2)
        data.add_data_point(f_list, list(j*ones(len(f_list))),list(i*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))

        data.new_block()
        spyview_process(data,start_f,stop_f,iteration, 1,j,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc

        #usage of ramy barends formula
        #format p: p[0]=w0, p[1]=Qi, p[2]=Qc, p[3]=unity transmission
        fitfunc_S21 = lambda p, x: p[3] + 20*np.log10(np.abs((float(p[2])/float(p[2]+p[1])-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))/(1-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))))
        errfunc = lambda p,x, y: fitfunc_S21(p,x)-y
        p0= [f_estimate,350,500,-66]
        p1, success = optimize.leastsq(errfunc,p0[:],args=(f_list,tr2))

        p1[1]=abs(p1[1])
        p1[2]=abs(p1[2])

        for z in p1:
            print z
            
        plot(f_list,tr2,"ro", f_list,fitfunc_S21(p1,f_list),"r-")


        # Legend the plot
        title("Transmission response of " + device_name + " timestap: " + date_path)
        xlabel("frequency [Hz]")
        ylabel("S21 transmission [dB]")
        legend(('data', 'fit'))
 
        ax = axes()
 
        text(0.8, 0.07,'f_res :  %.4f GHz \n Qi :  %u \n Qc : %u \n unity: %.1f dBm' % (p1[0]*1e-9,p1[1],p1[2],p1[3]),
                    fontsize=10,
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform=ax.transAxes)
    
        show()
        

data.close_file()

#adwin.set_DAC_1(0)
#adwin.set_DAC_2(0)

qt.mend()


#end of experiment routine

