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
med.set_device('uglyDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'OMIT_OMIA_pump_powerSweep'
data = qt.Data(name=filename)
data.add_coordinate('probe Frequency (MHz)')
data.add_coordinate('Cavity Frequency (MHz)')
data.add_coordinate('pump power (dBm)')

data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')
#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\post-Trieste\\20131027\\')
data.copy_file('OMIT_OMIA_pump_powerSweep.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#T 18 mK
# Gate = 0 / 4 V
# Cavity xx dBm +dircoup (direct) + isolator + direct dir coupler
## VNA drive has 40 + 8 + 10 (dir coup) + 37 inside
## Complicated carrier cancellation scheme see Log book entry 12/10/13 for the setup

## smb2 setup
## Cavity 2
#
hang_sp=5888.783#5974.077
hang_pt=1
hang_pow_st=30  # dBm
hang_pow_sp=10
hang_pow_pt=21


## PNA setup
pow_start=-25
f1_pts = 801
f1_bw = 5 #HZ
probe_f0=(5931.41)*MHz
probe_span=0.6*MHz
f1_start=probe_f0-probe_span/2
f1_stop=probe_f0+probe_span/2
probe_pt=f1_pts

pna.set_power(pow_start)
pna.set_resolution_bandwidth(f1_bw)
pna.set_sweeppoints(f1_pts)
pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)

########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
freq_list=np.linspace(hang_st,hang_sp,hang_pt)
pow_list=np.linspace(hang_pow_st,hang_pow_sp,hang_pow_pt)
#######################################################

count=0
for pw in pow_list:
    smb2.set_RF_power(pw)
    pw_dummy=np.linspace(pw,pw,len(f_list))
    for freq in freq_list:
        smb2.set_RF_frequency(freq)
        count=count+1
        print 'Power  NOW   '+str(pw)+'  Counter =  '+str(count)
        pna.sweep()
        fsv.set_center_frequency(freq)
        trace1= pna.fetch_data(polar=True)
        trace2= pna.fetch_data(polar=False)
        freq_dummy=np.linspace(freq,freq,len(f_list))
        data.add_data_point(pw_dummy,freq_dummy,f_list,trace1[0],trace1[1],trace2[0],trace2[1])
        data.new_block()
        spyview_process(data,f1_start,f1_stop,hang_pow_st,hang_sp,pw)
        qt.msleep(0.01)

#sweep_time = float(pna.q("SENS1:SWE:TIME?"))
data.close_file()
qt.mend()
