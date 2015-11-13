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
import pylab
#execfile('metagen2D.py')
execfile('metagen3D.py')
execfile('support_functions.py')


################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec


#Core variables
#start_freq = 5.155e9            #wide span
#stop_freq=5.450e9               #wide span
start_freq = 5.3219e9
stop_freq=5.3219e9
f_points =2
bandwidth=101
power = 0
averages=1

start_magv=10
stop_magv=-10
#mag_d = 0.04


start_gate = -10
stop_gate  = 10
#volt_step = 10
gate_points=401



flist=np.linspace(float(start_freq),float(stop_freq),f_points)




#magv_points = int((stop_magv - start_magv+1)/mag_d)

magv_points = 401
magvlist=np.linspace(float(start_magv),float(stop_magv),magv_points)


#gate_points = int((stop_gate - start_gate +1)/volt_step)
gatelist=np.linspace(float(start_gate),float(stop_gate),gate_points)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A_sal', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
#med.set_device('EOS8_C')
#med.set_setup('BF')
#med.set_user('Sal & Vibhor')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')

pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq,measurement_format = 'MLIN')
pna.set_power(power)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
pna.set_averages_on()
pna.set_averages(averages)
sweeptime = pna.get_sweeptime()*1.05

#adwin_DAC initialization
adwin.start_process()       #starts the DAC program
adwin.set_rampsteps(100)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Sal\\EOS8C\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed



#Set up data
filename = 'football_scan_adwin'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('V_gate (V)')
data.add_coordinate('V_adwin (V)')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('football_scan_adwin.py')

#Set up timing data
#filename_timing = 'football_scan_adwin_timing'
#data_timing = qt.Data(filename_timing)
#data_timing.add_coordinate('event')
#data_timing.add_value('time')
#data_timing.add_value('speed')

#data_timing.create_file(datadirs=base_path+date_path+'_____'+filename)


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

#timing variables
run_index=0
tstart = time()
t0= time()

x_time = 0
y_temp =0
exp_time = 0
measurement_time=0

prev_time=tstart
now_time=0
exp_number = len(magvlist)*averages*len(gatelist)


#start with DACs
adwin.set_DAC_2(magvlist[0])
adwin.set_DAC_1(gatelist[0])

qt.msleep(5)

print 'Start Experiment'

timing=[]
timing_div = []
#timing.append([tstart-t0,'start sweeping'])

tframe=time()

for magv in magvlist:
    print ' new frame: ', time()-tframe, '[s]', 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
    #med.set_frame_time(time()-tframe)
    
    new_outermostblockval_flag=True
    adwin.set_DAC_2(magv)
   
    for gate in gatelist:

        #print magv
        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time

        timing.append([now_time - t0,'start'])
        
        exp_time = exp_number*time_int
        if exp_time<0:
            exp_time = 60

        ave_list = np.linspace(1,averages,averages)

        #Set Voltage
        adwin.set_DAC_1(gate)
        #print 'wait to settle'
        #
        #qt.msleep(.2)
        #qt.msleep(.2*sweeptime)
        
        #print 'sweep'
        pna.reset_averaging()

        for i in ave_list:
            pna.sweep()
            pna.auto_scale()
            #qt.msleep(sweeptime)
            #print magv,i, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
        #clear pna
        timing.append([time()-t0,'post pna.sweep'])
        
    ##    
    ##    
    ##    for i in ave_list:
    ##        print 'sweep', i        
    ##        pna.sweep()
    ##        qt.msleep(sweeptime)
        trace=pna.fetch_data(polar=True)
        timing.append([time()-t0,'post fetch data 1'])
        tr2=pna.data_f()
        timing.append([time()-t0,'post data_f'])
        #tr2_parsed = pna.parse_trace(tr2)
        data.add_data_point(flist, list(gate*ones(len(flist))),list(magv*ones(len(flist))),trace[0], tr2, trace[1])

        data.new_block()
        spyview_process(data,start_freq,stop_freq,stop_gate, start_gate,magv,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
        timing.append([time()-t0,'after saving'])
        

data.close_file()

#adwin.set_DAC_1(0)
#adwin.set_DAC_2(0)

#save timging graph & possible save to file...

time_list =[]
time_div_list = []

start_bool=False
prev_time = 0

for i in timing:
    time_list.append(i[0])
    if(start_bool):
        time_div_list.append(i[0]-prev_time)
    start_bool = True
    prev_time=i[0]


#plot overall time list
pylab.close()
pylab.autoscale(tight=True)
pylab.plot(time_list)
pylab.savefig(base_path+date_path+'_____'+filename+'\\timing.png')
pylab.close()

time_analyses_points=5
analyse_list=np.linspace(0,time_analyses_points-1,time_analyses_points)

time_div_analyse=[]

for i in analyse_list:
    
    time_div_analyse.append(average(time_div_list[int(i)::int(time_analyses_points)]))


pylab.autoscale(tight=True)
pylab.plot(time_div_analyse)
pylab.savefig(base_path+date_path+'_____'+filename+'\\timing_div.png')
pylab.close()


qt.mend()

#end of experiment routine

