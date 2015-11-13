#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
#execfile('metagen3D_crazy.py')
execfile('metagen.py')

    
#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "installed instruments: "+" ".join(instlist)
#install the drivers no check

if 'med' not in instlist:
    med = qt.instruments.create('med','med')
#if 'pna' not in instlist:
#    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('uglyDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'OMIT_OMIA_UPDN_custom'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Power [dBm]')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')
#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\post-Trieste\\20131010\\')
data.copy_file('OMIT_OMIA_up_dn.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#T 14 mK
# Gate = 3.12 / 4 V
# Cavity 30 dBm +dircoup (direct) + isolator + 6dB adder
## VNA drive has 40 + 8 + 6 (adder) + 37 inside
## Complicated carrier cancellation scheme see Log book entry 10/10/13 for the setup


## smb2 setup
## Cavity 1 settings
##hang_st=5930.124 - 40.764 - 0.3  #MHz
##hang_sp=5930.124 - 40.764 + 0.3  #MHz
##hang_pt=201
##hang_pow=30  # dBm

## Cavity 2 settings
hang_st=5931.350 - 40.764 - 0.3  #MHz
hang_sp=5931.350 - 40.764 + 0.3  #MHz
hang_pt=101
hang_pow=30  # dBm


## PNA setup
pow_start=10
f1_pts = 1201
f1_bw = 100 #HZ


## Forward and backward sweep
## All settings needs to be set manually
## Here many points are for logging only


f1_start=5929.824*MHz # hanger_f0-hanger_span/2
f1_stop= 5930.424*MHz #hanger_f0+hanger_span/2

#adwin.start_process()
#adwin.set_DAC_2(3.12/4)

########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
rev=f_list[::-1]
comb_f_list = []
comb_f_list.extend(f_list)
comb_f_list.extend(rev)
freq_list=np.linspace(hang_st,hang_sp,hang_pt)
#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
#pna.reset_full() #proper reset command required to kill of bugs with the PNA
#pna.setup(measurement_type='S21',start_frequency=f1_start,stop_frequency=f1_stop, sweeppoints=(f1_pts),bandwidth=f1_bw,level=pow_start)
#pna.get_all() #get all the settings and store it in the settingsfile.
#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
# for speed turn off display 
# use 32bit data

####   EXPERIMENTAL AREA  ##########
#pna.set_averages_off()
#pna.set_averages(4)
#pna.w('SENS:AVER:MODE POIN') #for testing! set averaging mode to points (all chanals) sweep is the other option

#do a PNA testsweep
#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
#pna.sweep()

######################################

########## Print settings ################

#print 'step size: '+str((f1_stop-f1_start)/(f1_pts-1)) +' Hz'
#print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
#print 'averages of the pna: '+str(pna.get_averages())
#print 'sweeptime per trace (sec): '+str(sweep_time)

##################################################

print 'measurement loop:'

#pna.set_start_frequency(f1_start)
#pna.set_stop_frequency(f1_stop)
qt.msleep(0.1)
#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
count=0
for freq in freq_list:
    #pna.set_power(pw)
    smb2.set_RF_frequency(freq)
    count=count+1
    print 'Freq NOW   '+str(freq)+'  Counter =  '+str(count)
    pna.sweep()
    #qt.msleep(sweep_time)
    fsv.set_center_frequency(freq)
    trace1= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    freq_dummy=np.linspace(freq,freq,len(comb_f_list))
    data.add_data_point(freq_dummy,comb_f_list,trace1[0],trace1[1],trace2[0],trace2[1]) #for S21 vs power
    data.new_block()
    spyview_process(data,1,2402,freq)
    qt.msleep(0.01)

#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
data.close_file()
qt.mend()
