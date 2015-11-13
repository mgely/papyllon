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
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::192.168.1.42::inst0::INSTR')

if 'adwin' not in instlist:
    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#if 'smb' not in instlist:
#    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.1.25::INSTR')

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.25::inst0::INSTR')

#if 'fsv' not in instlist:
#    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136::inst0::INSTR')



instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('EOS8C')
med.set_setup('BF')
med.set_user('Vibhor & Sal')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

base_path = 'D:\\data\\Sal\\EOS8C\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)


filename = 'homodyne_gate_sweep'
data = qt.Data(name=filename)
data.add_coordinate('Frequency [MHz]')
data.add_coordinate('V_gate (Hz)')
data.add_value('S21 [abs]')
data.add_value('S21 [rad]')
data.add_value('S21 X')
data.add_value('S21 Y')
#data.create_file()
data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('homodyne_gate_sweep.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature
# Gate = 3.12 /4
#17 mK
## SMB2 on top with 1 dB + 37 att
## PNA drive has 40 + 8 + 6 +37
## Carrier Cancellation + 1 Miteq in action

## PNA settings

f_cw = 5321.68*MHz

pow_start=30
f1_pts = 5001
f1_bw = 200 #HZ
start_f = 10*MHz
stop_f = 100*MHz

### Gate settings
gate_start=0
gate_stop=10
gate_pt=101
#adwin.set_DAC_2(gate_start)

## Preparing hanger
smb2.set_RF_frequency(f_cw/MHz)
smb2.set_RF_power(8)
smb2.set_RF_state(True)


''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
#pna.reset() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=start_f,stop_frequency=stop_f, sweeppoints=(f1_pts),bandwidth=f1_bw,level=pow_start)
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


f_list=np.linspace(float(start_f),float(stop_f),(f1_pts))
gate_list=np.linspace(gate_start,gate_stop,gate_pt)

##################################################

pna.set_start_frequency(start_f)
pna.set_stop_frequency(stop_f)
qt.msleep(0.1)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
for gate in gate_list:
    print 'current gate '+str(gate)+' Volt'
    adwin.set_DAC_1(gate)

    qt.msleep(1)
    pna.sweep()
    trace= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    gate_dummy=np.linspace(gate,gate,len(f_list))
    data.add_data_point(gate_dummy,f_list,trace[0],trace[1],trace2[0],trace2[1])
    data.new_block()
    spyview_process(data,start_f,stop_f,gate)
    qt.msleep(0.01)
data.close_file()
qt.mend()
