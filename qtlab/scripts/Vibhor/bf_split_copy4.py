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

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136::inst0::INSTR')



instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'Norm_mode_split'
data = qt.Data(name=filename)
data.add_coordinate('Cavity freq [MHz]')
data.add_coordinate('Frequency [MHz]')
data.add_value('S21 [abs]')
data.add_value('S21 [rad]')
data.add_value('S21 X')
data.add_value('S21 Y')
#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\neatDrum\\20140218\\')
data.copy_file('bf_split_copy4.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature
# Gate = 0
#14 mK
## SMB2 on top with 1 dB + 37 att
## PNA setup 4th FEb
## 
## See log book entry for complete setup

## PNA settings

pow_start=-10
f1_pts = 1001
f1_bw = 100 #HZ
hanger_f0=5900.579*MHz
hanger_span=500*kHz
f1_start=hanger_f0-hanger_span/2
f1_stop=hanger_f0+hanger_span/2

## Cavity settings
hang_st=5900.6 - 131  #MHz
hang_sp=5900.6 - 171  #MHz
hang_pt=1601
hang_pow=26  # dBm

## Preparing hanger
smb2.set_RF_frequency(hang_st)
smb2.set_RF_power(hang_pow)
smb2.set_RF_state(True)


''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=f1_start,stop_frequency=f1_stop, sweeppoints=(f1_pts),bandwidth=f1_bw,level=pow_start)
pna.get_all() #get all the settings and store it in the settingsfile.
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
# for speed turn off display 
# use 32bit data

####   EXPERIMENTAL AREA  ##########
print 'set experimental stuf, point averages, ...'
pna.set_averages_off()
#pna.set_averages(4)
#pna.w('SENS:AVER:MODE POIN') #for testing! set averaging mode to points (all chanals) sweep is the other option

#do a PNA testsweep
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
#pna.sweep()


########### making lists of values to be measured ###########

hang_f_list=np.linspace(hang_st,hang_sp,hang_pt)
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
#gate_list=np.linspace(gate_start,gate_stop,gate_pt)

##################################################

pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)
qt.msleep(0.1)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
for hf in hang_f_list:
    print 'current freq '+str(hf)+' Volt'
    smb2.set_RF_frequency(hf)
    fsv.set_center_frequency(hf)
    qt.msleep(1)
    pna.sweep()
    trace= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    hf_dummy=np.linspace(hf,hf,len(f_list))
    data.add_data_point(hf_dummy,f_list,trace[0],trace[1],trace2[0],trace2[1])
    data.new_block()
    spyview_process(data,f1_start,f1_stop,hf)
    qt.msleep(0.01)
data.close_file()
qt.mend()
