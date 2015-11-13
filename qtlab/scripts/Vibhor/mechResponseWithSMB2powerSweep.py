#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('meta3d.py')   #to create meta files
#execfile('ramp.py')     #allows to slowly ramp a value

    
#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "installed instruments: "+" ".join(instlist)
#install the drivers no check

if 'med' not in instlist:
    med = qt.instruments.create('med','med')
if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')


instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

filename = 'mechResponseWithSMB2powerSweep'
data = qt.Data(name=filename)
data.add_coordinate('probe Frequency (MHz)')
data.add_coordinate('Cavity Frequency (MHz)')
data.add_coordinate('pump power (dBm)')

data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')
base_path = 'D:\\data\\Vibhor\\neatDrum\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('mechResponseWithSMB2powerSweep.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#T 13 mK
# Gate =  -2 V
# Cavity power to be swept @ 5900.5 see log book for detalied ckt
## ## see Log book entry 1/4/14 new ckt for the setup
## HEMT + Miteq+2HP filter+17dBm LO from a different smb
## Mnckt mixer


## SMB2 setup
hang_st=5900.5
hang_sp=5900.5#
hang_pt=1
hang_pow_st=3  # dBm
hang_pow_sp=-33
hang_pow_pt=13


## PNA setup
pow_start=-2
f1_pts = 401
f1_bw = 500 #HZ
probe_f0=(35.76756)*MHz
probe_span=0.080*MHz
f1_start=probe_f0-probe_span/2
f1_stop=probe_f0+probe_span/2
probe_pt=f1_pts

pna.set_power(pow_start)
pna.set_resolution_bandwidth(f1_bw)
pna.set_sweeppoints(f1_pts)
pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)
pna.w("SENS:AVER:CLE")

########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
freq_list=np.linspace(hang_st,hang_sp,hang_pt)
pow_list=np.linspace(hang_pow_st,hang_pow_sp,hang_pow_pt)
#######################################################

for pw in pow_list:
    smb2.set_RF_power(pw)
    pw_dummy=np.linspace(pw,pw,len(f_list))
    for freq in freq_list:
        smb2.set_RF_frequency(freq)
        count=count+1
        print 'Power  NOW   '+str(pw)+'  Counter =  '+str(count)
        #pna.sweep()
        pna.set_averages_on()
        pna.set_averages(1200)
        pna.w('SENS:AVER:MODE SWEEP') #set avg type to SWEEP / POINT
        qt.msleep(240)
        #fsv.set_center_frequency(freq)
        trace1= pna.fetch_data(polar=True)
        trace2= pna.fetch_data(polar=False)
        freq_dummy=np.linspace(freq,freq,len(f_list))
        data.add_data_point(pw_dummy,freq_dummy,f_list,trace1[0],trace1[1],trace2[0],trace2[1])
        data.new_block()
        spyview_process(data,f1_start,f1_stop,hang_pow_st,hang_sp,pw)
        qt.msleep(0.01)
        pna.w("SENS:AVER:CLE")

data.close_file()
qt.mend()
