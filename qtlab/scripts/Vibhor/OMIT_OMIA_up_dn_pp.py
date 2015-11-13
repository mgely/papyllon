#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen3D.py')
#execfile('metagen.py')

    
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
med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'OMIT_OMIA_UPDN_pp'
data = qt.Data(name=filename)
data.add_coordinate('Probe Frequency (MHz)')
data.add_coordinate('Drive Frequency (MHz)')
data.add_coordinate('probe power (dBm)')

data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')

base_path = 'D:\\data\\Vibhor\\NeatDrum highPower\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('OMIT_OMIA_up_dn_pp.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature
# Gate = 0
#while cooling
## 37 inside return + HEMT 
## Check log book entry 1st September


## SIDE BAND DRIVE VARIABLES

hang_st=5864.180-0.200
hang_sp=5864.180+0.200
hang_pt=101
hang_pow=11  # dBm

## PNA setup
pow_start=-2
pow_stop=16
pow_pts=7
f1_pts = 2001
f1_bw = 300 #HZ
pna.set_power(pow_start)
pna.set_resolution_bandwidth(f1_bw)

probe_f0=(5900.55)*MHz
probe_span=0.40*MHz
f1_start=probe_f0-probe_span/2
f1_stop=probe_f0+probe_span/2
probe_pt=f1_pts

## Arbitrary sweep ON
##pna.w('SENS:SGM:ARB ON')

## Setting up table 
pna.w('SENS:FOM:RANG:SEGM1:FREQ:STAR '+str(f1_start))
pna.w('SENS:FOM:RANG:SEGM1:FREQ:STOP '+str(f1_stop))
pna.w('SENS:FOM:RANG:SEGM1:SWE:POIN '+str(probe_pt))
pna.w('SENS:FOM:RANG:SEGM2:FREQ:STAR '+str(f1_stop))
pna.w('SENS:FOM:RANG:SEGM2:FREQ:STOP '+str(f1_start))
pna.w('SENS:FOM:RANG:SEGM2:SWE:POIN '+str(probe_pt))

#adwin.start_process()
#adwin.set_DAC_2(0/4)

########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
rev=f_list[::-1]
comb_f_list = []
comb_f_list.extend(f_list)
comb_f_list.extend(rev)
freq_list=np.linspace(hang_st,hang_sp,hang_pt)
pow_list=np.linspace(pow_start,pow_stop,pow_pts)
bw_list=[200,200,300,500,1000,1500,3000]
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
for pw in pow_list:
    pw_dummy=np.linspace(pw,pw,len(comb_f_list))
    print 'power = '+str(pw)
    pna.set_power(pw)
    if -30<pw<=-2:
        pna.set_resolution_bandwidth(200)
        print 'setting BW to '+str(200)
    elif -2<pw<=1:
        pna.set_resolution_bandwidth(200)
        print 'setting BW to '+str(200)
    elif 1<pw<=4:
        pna.set_resolution_bandwidth(300)
        print 'setting BW to '+str(300)
    elif 4<pw<=7:
        pna.set_resolution_bandwidth(500)
        print 'setting BW to '+str(500)
    elif 7<pw<=10:
        pna.set_resolution_bandwidth(1000)
        print 'setting BW to '+str(1000)
    elif 10<pw<=13:
        pna.set_resolution_bandwidth(150)
        print 'setting BW to '+str(1500)
    elif 13<pw<=16:
        pna.set_resolution_bandwidth(3000)
        print 'setting BW to '+str(3000)

    for freq in freq_list:
        smb2.set_RF_frequency(freq)
        count=count+1
        print 'Freq NOW   '+str(freq)+'  Counter =  '+str(count)
        pna.sweep()
        #qt.msleep(sweep_time)
        #fsv.set_center_frequency(freq)
        trace1= pna.fetch_data(polar=True)
        trace2= pna.fetch_data(polar=False)
        freq_dummy=np.linspace(freq,freq,len(comb_f_list))
        data.add_data_point(pw_dummy,freq_dummy,comb_f_list,trace1[0],trace1[1],trace2[0],trace2[1])

        data.new_block()
        qt.msleep(0.01)
        #spyview_process(data,1,2*probe_pt,-1.0,1.0,pw)
        qt.msleep(0.01)

#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
data.close_file()
qt.mend()
