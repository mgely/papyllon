#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('meta3d.py')

    
med = qt.instruments.create('med','med')
pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')
smb = qt.instruments.create('smb','RS_SMB100A', address='TCPIP0::192.168.1.131::inst0::INSTR')
smb2 = qt.instruments.create('smb','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')

med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor & Ben')


qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

filename = 'RD_V01'
data = qt.Data(name=filename)
data.add_coordinate('Points')
data.add_coordinate('CW_freq')
data.add_coordinate('CW_pow')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 [X]')
data.add_value('S21 [Y]')
base_path = 'D:\\data\\Vibhor\\neatDrum\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('bf-PNA_trace_ringdown.py')

##############         Variables to set
kHz = 1e3
MHz = 1e6

avg = 2000
time = 6.221*1e-3 #0.005 #sec
bw = 200*kHz #Hz
pulse_width = 1000 #usec
pulse_period = 2000 #usec
points = 1001
time_dummy=np.linspace(0,points-1,points)

freq = 5900.586*MHz #Hz
span = 100*kHz #Hz
f_points = 101
f_start = freq-span/2.0 #Hz
f_stop = freq+span/2.0 #Hz
freq_list=np.linspace(f_start,f_stop,f_points)

p_start = -15
p_stop = -15
p_points = 1
p_list=np.linspace(p_start,p_stop,p_points)

drive_f=5864.344 # MHz
drive_power=28 #MHz


########################
spyview_process(data,
                len(time_dummy),
                0,
                points-1,
                len(freq_list),
                f_stop,
                f_start,
                len(p_list),
                p_start,
                p_stop)
############################

print 'Prepare SMB'
smb.get_all()
smb.set_reference('EXT')
smb.set_pulse_period(pulse_period) #us
smb.set_pulse_width(pulse_width) #us
smb.set_pulse_state(True)
smb.set_RF_state(False)

print 'Prepare smb2'
smb2.set_RF_frequency(drive_f)
smb2.set_RF_power(drive_power)
smb2.set_RF_state(True)

print 'Prepare PNA'
#reset PNA
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.reset()
#set display
pna.w("DISP:WIND1:STATE ON")
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.w("DISP:WIND1:TRACE1:FEED 'CH1_S21_S1'")
#set triger
pna.w("TRIG:SOUR EXT") #set trig to ext
pna.w("TRIG:TYPE EDGE") #set to trig on edge
pna.w("TRIG:SLOP POS") #pos edge trig
#setup CW and averaging
pna.w("SENS:SWE:TYPE CW") #Set CW type
pna.w('SENS:FREQ '+str(freq))
pna.set_averages_on()
pna.set_averages(avg)
pna.w('SENS:AVER:MODE SWEEP') #set avg type to SWEEP / POINT
#set sweep
pna.set_power(p_start)
pna.set_sweeppoints(points)
pna.set_resolution_bandwidth(bw)
pna.set_sweeptime(time)
pna.get_all() #get all the settings and store it in the settingsfile.
#get ready
pna.w("SENS:AVER:CLE") #clear prev averages
sweep_time = float(pna.q("SENS1:SWE:TIME?"))

print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
print 'averages of the pna: '+str(pna.get_averages())
print 'sweeptime per trace (sec): '+str(sweep_time)
print 'measurement loop:'

for p in p_list:
    pna.set_power(p)
    print p
    p_dummy=np.linspace(p,p,points)
    for f in freq_list:
        print f/1.0e6
        freq_dummy=np.linspace(f,f,points)
        pna.w('SENS:FREQ '+str(f))
        pna.w("SENS:AVER:CLE")
        sweep_time = float(pna.q("SENS1:SWE:TIME?"))
        qt.msleep(avg*sweep_time)
        trace= pna.fetch_data(polar=True)
        trace2= pna.fetch_data(polar=False)
        data.add_data_point(p_dummy,freq_dummy,time_dummy,trace[0],trace[1],trace2[0],trace2[1])
        data.new_block()

data.close_file()
qt.mend()
