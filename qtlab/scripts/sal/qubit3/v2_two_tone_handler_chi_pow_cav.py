#################################################
##########          Two tone run file
################################################

# Author SJ Bosman
# Experiment script for doing two tone spectroscopy on qubit/cpb
# Basic structure:
# Define the core variables
# Setup the instruments & data structure
#
# Experiment loop:
# 1) the main variable is the Chi, which is the cavity Stark shift (typically ~.1MHz)
# 2) First it is checked if the qubit is Biased such that Chi is what it should be (channel 1 PNA)
# 3) Then a segment of the probe_frequency is swept (channel 2 PNA)
# 4) Then we check if the qubit is still at his bias point, if yes then we move to the next segment
# 5) If not then we refind the qubit bias and redo the segment

# the supplementary functions and settings are stored in the pna_setup_two_tone.py script.


################################################
#               Development notes
################################################

# also implement a gate search that overshoots a bit on chi and then goes back to the optimum.
# or even better it, walks based on the change in starkshift it goes gate_list.index+/-1 to reach quicker
# the maximum and not to change the gate too fast.
#check with the derivative of the starkshift wheter qubit is above or below cavity.
# implement a segment sweep succeed bool array and keep statistics..
# timing module
# tcp ip terminal for the iphone / watch a log & be able to send commands dynamically.


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

##################################################
####            Core variables
##################################################

w_bare=5.3217e9

#magnetic field Variable
magv=-7.93846

#Bias monitor
bias_start_cav = 5.319e9
bias_stop_cav = 5.323e9
bias_f_points = 121
bias_ifbw = 100
bias_pow  = 10
bias_aver_cav = 1

bias_aver_cav_list = np.linspace(1,1,aver_cav)





#Chi - AC Stark shift
#chi=-1e6
#my_chi=chi


#bias_error=150e3
#start_chi = -1e6
#stop_chi = 0
#chi_points = 21
#chi_list = np.linspace(start_chi, stop_chi, chi_points)

chi_list=[-3.4e6,-2.0e6,-1.6e6,-1.3e6,-1.1e6,-.95e6,-.8e6,-.75e6,-.6e6,-.56e6,-.5e6,-.42e6,-.36e6,-.322e6,-.261e6,-.201e6,-.14e6]

magv_list=[-7.69,-7.73,-7.77,-7.8,-7.85,-7.88,-7.92,-7.96,-8,-8.03,-8.12,-8.15,-8.31,-8.46,-8.69,-8.85,-9]

#Probe power
#start_probe_power = 20
#stop_probe_power = -30
#power_probe_points=12
#probe_power_list = np.linspace(start_probe_power,stop_probe_power,power_probe_points)
probe_power=6


#Cavity power
start_cav_power = 10
stop_cav_power = -30
power_points=9

cav_power_list = np.linspace(start_cav_power,stop_cav_power,power_points)


#gate
start_gate = -2.25
stop_gate  = 2.25
gate_points=81
gatelist=np.linspace(float(start_gate),float(stop_gate),gate_points)

#Two tone experiment
f_cw = w_bare+chi
pow_cw = cav_power_list[0]


#Probe frequency variables.
start_probe = 5.5e9
stop_probe=6.5e9
f_points_probe =501
ifbw_probe=101
aver_probe=150

segment_length = 11

segment_succes=[]

probe_list=np.linspace(start_probe,stop_probe,f_points_probe)

probe_segments =[probe_list[x:x+segment_length] for x in xrange(0, len(probe_list), segment_length)]

print 'probe_list: \t' + str(f_points_probe) + '\t segment_length: \t' + str(segment_length) + '\t number of segments: \t' + str(len(probe_segments))

#setup instruments
execfile('v2_pna_setup_two_tone.py')

###set magnetic field to
adwin.set_DAC_2(magv)


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
filename = 'two_tone_handler_chi_pow_cav'
data = qt.Data(name=filename)
data.add_coordinate('Probe Frequency (MHz)')
data.add_coordinate('Chi (MHz')
data.add_coordinate('Cavity power (dBm)')
data.add_value('Real (dBm)')
data.add_value('Img [dBm]')

path = base_path+date_path+'_____'+filename


data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('two_tone_handler_chi_pow_cav.py')
data.copy_file('pna_setup_two_tone.py')


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
#exp_number = len(magvlist)*averages*len(gatelist)

segment_index=0
frame_index=0

probe_data =[[],[]]
new_outermostblockval_flag=False

bias_error=.1e6
for cav_power in cav_power_list:


    #set programmatic variables
    frame_index=frame_index+1
    new_outermostblockval_flag=True

    #output info
    print 'Frame:', str(frame_index), '/', len(cav_power_list), '\t probe power: ', str(cav_power) 

    #set machines
    pna.w("SOUR2:POW1 %s" %(cav_power))    
    
    line_index=0
    for my_chi in chi_list:

        line_index=line_index+1
        print 'Line:', str(line_index), '/', len(chi_list), '\t cavity power: ', str(my_chi)

        #set magv
        adwin.set_DAC_2(magv_list[line_index-1])        #check if it corresponds
        #wait

        #set f_cw to w_bare+chi
        pna.w("SENS2:FOM:RANG3:FREQ:CW %s" %(f_cw + my_chi)) #set cw freq to receivers
        pna.w("SENS2:FOM:RANG2:FREQ:CW %s" %(f_cw + my_chi)) #set cw freq to source1
        
        segment_index = 0 
        
        #bias_monitor=False
        for segment in probe_segments:
            segment_index=segment_index+1
            
            segment_unfinished=True
            bias_found=False

            while(segment_unfinished):

                print 'start segment loop'
                if(check_bias(chi=my_chi, error=bias_error)):
                    print 'start a new segment \t no: ' + str(segment_index) + '\t of total:\t' + str(len(probe_segments))
                
                    pna.w("SENS2:FREQ:START %s" % (segment[0]))
                    print 'start segment at \t' + to_GHz(segment[0]) + '\t GHz'
                    
                    pna.w("SENS2:FREQ:STOP %s" % (segment[-1]))
                    print 'stop segment at \t' + to_GHz(segment[-1]) + '\t GHz'
                    
                    pna.w("SENS2:SWE:POIN %s" % (len(segment)))

                    pna.trigger(channel=2)      #trigger sweep for this segment
                    pna.auto_scale(window=2,trace=1)
                    bias_ok = check_bias(chi=my_chi, error=bias_error)      #check if the bias was still ok.
                    if(bias_ok):
                          segment_succes.append(True)
                          print 'segment sweep succeeded \t \t succes rate:' + str(round(np.array(segment_succes).mean(),2)*100)+'%'
                          
                          temp = pna.fetch_data(channel=2,polar=True)
                          probe_data=[np.concatenate([probe_data[0],temp[0]]),np.concatenate([probe_data[1],temp[1]])]
                          
                          segment_unfinished=False
                    else:
                          segment_succes.append(False)
                          print 'redo segment scan \t\t succes rate: ' + str(round(np.array(segment_succes).mean(),2)*100)+'%'
                          bias_monitor=False

                else:
                    if(find_balanced_bias(chi=my_chi,error=bias_error, center_gate_index=gatelist.searchsorted(adwin.get_DAC_1()))):
                        print 'balanced bias found'
                        bias_found=True
                    else:
                        print 'find bias traditionally'
                        bias_found=find_bias(chi=my_chi,error=bias_error)
                        

        #store qt lab data
        my_chi_dummy = np.linspace(my_chi,my_chi,len(probe_list))
        cav_power_dummy = np.linspace(cav_power,cav_power,len(probe_list))
        data.add_data_point(probe_list, my_chi_dummy, cav_power_dummy, probe_data[0],np.unwrap(probe_data[1]))
        data.new_block()

        #reset variables
        probe_data=[[],[]]
        spyview_process(data,start_probe,stop_probe,stop_cav_power,start_cav_power,my_probe_power,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False

data.close_file()     
qt.mend()
