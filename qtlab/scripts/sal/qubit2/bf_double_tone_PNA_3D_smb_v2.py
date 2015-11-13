################################
#       DESCRIBTION
################################

#Measurement script that does single tone qubit spectroscopy using the ADwin
#as a DAC to either sweep magnetic field of gate voltage.

timing = []



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

t0=time()

timing.append([t0,'t0'])

################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec


#Core variables
start_freq = 5.315e9
stop_freq=5.33e9
f_points =51
bandwidth=501
power = -5
averages=1

start_probe = 5.3e9
stop_probe = 3e9
probe_step = .2e6
probe_power = 10

I_bias = -6.53
V_bias = -5


flist=np.linspace(float(start_freq),float(stop_freq),f_points)


probe_points = int(np.abs((stop_probe - start_probe+1))/probe_step)
probe_list=np.linspace(float(start_probe),float(stop_probe),probe_points)

explist=np.linspace(1,100,100)

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='TCPIP::192.168.1.25::INSTR')


#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS8_C')
med.set_setup('BF')
med.set_user('Sal & Vibhor')

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

#smb
smb.set_RF_frequency(probe_list[0]/1e6)
smb.set_RF_power(probe_power)
smb.set_reference('EXT')
smb.set_RF_state(True)

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
filename = 'bf_double_tone_PNA_3D_smb_v2'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('Probe Frequency (MHz)')
data.add_coordinate('sweep')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('bf_double_tone_PNA_3D_smb_v2.py')


spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
tstart = time()

x_time = 0
y_temp =0
measurement_time=0

print 'Start Experiment'
#qt.msleep(5)

def display_time(time):
    hours = time/3600
    minutes = (time-3600*floor(hours))/60
    seconds = (time-3600*floor(hours)-60*floor(minutes))

    return hours, ':', minutes, ':', seconds
    

#variables
run_index=0
tstart = time()

prev_time=tstart
now_time=0
exp_number = len(magvlist)*averages*len(gatelist)

adwin.set_DAC_2(I_bias)
adwin.set_DAC_1(V_bias)

print 'Start sweeping'

timing.append([tstart-t0,'start sweeping'])

tframe=time()

for exp in explist:
    print ' new frame: ', time()-tframe, '[s]', 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
    med.set_frame_time(time()-tframe)
    
    new_outermostblockval_flag=True
   
    for probe in probe_list:
        #print magv
        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time

        timing.append([now_time - t0,magv])
        
        exp_time = exp_number*time_int
        if exp_time<0:
            exp_time = 60

        ave_list = np.linspace(1,averages,averages)


        #set probe frequency
        smb.set_RF_frequency(probe/1e6)
        
        qt.msleep(.2)
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
        data.add_data_point(flist, list(exp*ones(len(flist))),list(probe*ones(len(flist))),trace[0], tr2, trace[1])

        data.new_block()
        spyview_process(data,start_freq,stop_freq,stop_probe, start_probe,exp,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
        timing.append([time()-t0,'after saving'])
        

data.close_file()

adwin.set_DAC_1(0)
adwin.set_DAC_2(0)

qt.mend()

timing.append([time()-t0,'end of exp'])
#end of experiment routine

