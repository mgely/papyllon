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


#cavity tone
start_cav = 5.3175e9
stop_cav = 5.3255e9
f_points_cav = 51
ifbw_cav = 10
pow_cav  = -10
aver_cav = 10

#probe tone
f_cw = 5.3222e9

start_probe = 5.5e9
stop_probe = 6e9
f_points_probe = 1001
ifbw_probe = 10
pow_probe = -20
aver_probe = 10

#magnetic field
start_magv=-6.9
stop_magv=-6.7
#mag_d = 0.04

#gate 
start_gate = -.5
stop_gate  = -.7
#volt_step = 10
gate_points=20



fp_list=np.linspace(float(start_probe),float(stop_probe),f_points_probe)
fcav_list=np.linspace(float(start_cav),float(stop_cav),f_points_cav)


#magv_points = int((stop_magv - start_magv+1)/mag_d)
magv_points = 20

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


#adwin_DAC initialization
adwin.start_process()       #starts the DAC program
adwin.set_rampsteps(100)

#PNA INIT
#setup two windows
pna.reset()

#setup two displays
pna.w("DISP:WIND1:STATE ON")
pna.w("DISP:WIND2:STATE ON")

pna.w("INIT:CONT OFF")          #switch to manual triggering, it triggers all channels globally

#setup cavity scan (magnitude)
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.w("DISP:WIND1:TRACE1:FEED 'CH1_S21_S1'")
pna.w("CALC1:PAR:SEL 'CH1_S21_S1'")
pna.w("CALC1:FORM MLOG")



##
###setup cavity (real)
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_REAL','B,1'")
pna.w("DISP:WIND1:TRACE2:FEED 'CH1_S21_REAL'")
pna.w("CALC1:PAR:SEL 'CH1_S21_REAL'")
pna.w("CALC1:FORM REAL")
#qt.msleep(20)       #wait for first trace to complete
pna.w("DISP:WIND1:TRACE2:Y:SCAL:AUTO")
pna.w("DISP:WIND1:TRACE1:Y:SCAL:AUTO")

pna.w("SENS:FREQ:START %s" % (start_cav))
pna.w("SENS:FREQ:STOP %s" % (stop_cav))
pna.w("SENS:SWE:POIN %s" % (f_points_cav))
pna.w("SENS:BWID %s" % (ifbw_cav))
pna.w("SENS:AVER 1")
pna.w("SENS:AVER:MODE POIN")
pna.w("SENS:AVER:COUN %s" % (aver_cav))

#do peak detection
pna.w("CALC1:MARK ON")
pna.w("CALC1:MARK:FUNC MAX")
pna.w("CALC1:MARK:FUNC:TRAC ON")

##
###setup two tone scan
pna.w("CALC2:PAR:DEF:EXT 'CH2_S21_S1', 'B,1'")
pna.w("DISP:WIND2:TRACE1:FEED 'CH2_S21_S1'")
pna.w("CALC2:PAR:SEL 'CH2_S21_S1'")

pna.w("SENS2:FREQ:START %s" % (start_probe))
pna.w("SENS2:FREQ:STOP %s" % (stop_probe))
pna.w("SENS2:SWE:POIN %s" % (f_points_probe))
pna.w("SENS2:BWID %s" % (ifbw_probe))
pna.w("SENS2:AVER 1")
pna.w("SENS2:AVER:MODE POIN")
pna.w("SENS2:AVER:COUN %s" %(aver_probe))
#still switch averaging on


pna.w("SENS2:FOM:STATE 1")      #switch on Frequency Offset Module
pna.w("SENS2:FOM:RANG3:COUP 0")     #decouple Receivers
pna.w("SENS2:FOM:RANG2:COUP 0")     #decouple Source 

pna.w("SENS2:FOM:RANG3:SWE:TYPE CW")    #set Receivers in CW mode
pna.w("SENS2:FOM:RANG2:SWE:TYPE CW")    #set Source in CW mode

pna.w("SENS2:FOM:RANG3:FREQ:CW %s" %(f_cw)) #set cw freq
pna.w("SENS2:FOM:RANG2:FREQ:CW %s" %(f_cw)) #set cw freq

pna.w("SENS2:FOM:DISP:SEL 'Primary'")       #set x-axis to primary 

pna.w("SOUR2:POW:COUP 0")                   #decouple powers
pna.w("SOUR2:POW1 %s" %(pow_cav))
pna.w("SOUR2:POW3 %s" %(pow_probe))
pna.w("SOUR2:POW3:MODE ON")                 #switch on port3


#### set triggering per channel
pna.w("SENS1:SWE:MODE HOLD")
pna.w("SENS1:SWE:MODE HOLD")
pna.w("TRIG:SCOP CURR")

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Sal\\EOS8C\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)




#Set up probe_tone data
filename = 'two_tone_q_spectroscopy'
data = qt.Data(name=filename)
data.add_coordinate('Probe Frequency (MHz)')
data.add_coordinate('V_gate (V)')
data.add_coordinate('V_adwin (V)')
data.add_value('Real (dBm)')
data.add_value('Img [dBm]')


path = base_path+date_path+'_____'+filename


data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('two_tone_q_spectroscopy.py')

#Set up cavity data
filename_cav = 'two_tone_q_spectroscopy_cav'
data_cav = qt.Data(name=filename_cav)
data_cav.add_coordinate('Cavity Frequency (MHz)')
data_cav.add_coordinate('V_gate (V)')
data_cav.add_coordinate('V_adwin (V)')
data_cav.add_value('Transmission (MLIN)')
data_cav.add_value('Phase')

data_cav.create_file(datadirs=base_path+date_path+'_____'+filename_cav)


spyview_process(reset=True)

##################
###  PNA setup
##################


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
peak_list=[]

for magv in magvlist:
    print ' new frame: ', time()-tframe, '[s]', 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
    #med.set_frame_time(time()-tframe)
    
    new_outermostblockval_flag=True
    print 'set mag field'
    adwin.set_DAC_2(magv)
   
    for gate in gatelist:

        print 'set gate'
        ######
        #   settings
        #######
        adwin.set_DAC_1(gate)


        #timing
        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time

        timing.append([now_time - t0,'start'])
        
        exp_time = exp_number*time_int
        if exp_time<0:
            exp_time = 60


        ###################
        ###     do cavity measurement
        ###################
        ave_cav_list = np.linspace(1,aver_cav,aver_cav)
        #pna.reset_averaging()
        pna.w("SENS1:AVER:CLE")
        pna.w("SENS2:AVER:CLE")
        
        print 'reset pna averaging'
        #pna.sweep()
        pna.w("INIT1:IMM")

        while a==0:
            qt.msleep(0.05)
            try:
                a=eval(self.q('*OPC?;'))
                break
            except(KeyboardInterrupt, SystemExit):
                raise
            except:
                a=0
        
        pna.w("DISP:WIND1:TRACE2:Y:SCAL:AUTO")
        pna.w("DISP:WIND1:TRACE1:Y:SCAL:AUTO")
        #pna.w("DISP:WIND2:TRACE1:Y:SCAL:AUTO")
            
        print magv,i, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
        #clear pna
        timing.append([time()-t0,'post pna.sweep'])
        
        #store cavity data
        trace_cav=pna.fetch_data(channel=1,polar=False)
        gate_cav_dummy=np.linspace(gate,gate,len(fcav_list))
        magv_cav_dummy=np.linspace(magv,magv,len(fcav_list))

        data_cav.add_data_point(fcav_list,gate_cav_dummy,magv_cav_dummy,trace_cav[0],trace_cav[1])
        data_cav.new_block()
        spyview_process(data_cav,start_cav,stop_cav,stop_gate,start_gate,magv,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False

        #get f_cw for these settings
        pna.w("CALC1:MARK ON")
        pna.w("CALC1:MARK:FUNC MAX")
        pna.w("CALC1:MARK:FUNC:TRAC ON")
        f_cw=pna.q("CALC1:MARK:X?")
        #peak_list.append([magv,gate,f_cw])


        pna.w("SENS2:FOM:RANG3:FREQ:CW %s" %(f_cw)) #set cw freq
        pna.w("SENS2:FOM:RANG2:FREQ:CW %s" %(f_cw)) #set cw freq

        pna.w("INIT2:IMM")
        while a==0:
            qt.msleep(0.05)
            try:
                a=eval(self.q('*OPC?;'))
                break
            except(KeyboardInterrupt, SystemExit):
                raise
            except:
                a=0
        
        #store probe data
        trace_probe=pna.fetch_data(channel=2,polar=True)
        gate_p_dummy=np.linspace(gate,gate,len(fp_list))
        magv_p_dummy=np.linspace(magv,magv,len(fp_list))

        data.add_data_point(fp_list, gate_p_dummy, magv_p_dummy, trace_probe[0],trace_probe[1])
        data.new_block()
        spyview_process(data,start_probe,stop_probe,stop_gate,start_gate,magv)      #do not update outermostblockval 


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

