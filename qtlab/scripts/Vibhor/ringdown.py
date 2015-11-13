#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('meta3d.py')   #to create meta files
execfile('ramp.py')     #allows to slowly ramp a value


med = qt.instruments.create('med','med')

instlist = qt.instruments.get_instrument_names()
smb = qt.instruments.create('smb','RS_SMB100A', address='TCPIP0::192.168.1.131::inst0::INSTR')
smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')
if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')
pna.get_all() #update old values

vi = qt.instruments.create('vi','virtual_composite')
vi.add_variable_scaled('Vg', pna, 'dac1', 1.0/0.2/4, 0.0)
def sweep(var='none',val=0):
    if var == 'Vg':
        ramp(vi,'Vg',val,0.05,0.1) #ramp (value,sweepstep,sweeptime)
    else:
        print 'No variable given'


med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor & Ben')


qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

filename = 'Homodyne'
data = qt.Data(name=filename)

data.add_coordinate('time')
data.add_coordinate('CW_freq det [GHz]')
data.add_coordinate('CW_pow')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 [X]')
data.add_value('S21 [Y]')
base_path = 'D:\\data\\Vibhor\\neatDrum\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('ringdown.py')

##############         Variables to set
kHz = 1e3
MHz = 1e6

#Pulse
pulse_width = 7500#500 #usec
pulse_period = 15000#1000 #usec

#AVG, BW, and Points
avg = 8200
bw = 600*kHz#600*kHz #Hz
wait_time = 240.0 #How long it will average in sec
points = 915 #number of Time points
time_dummy=np.linspace(0,1,points)

#PNA Probe frequency
freq = 33.653305*MHz #585841*MHz #Hz
span = 50.0*kHz#50*kHz #Hz
f_points = 501
f_start = freq-span/2.0 #Hz
f_stop = freq+span/2.0 #Hz
freq_list=np.linspace(f_start,f_stop,f_points)

#PNA Probe drive # Switches on Probe arm # 20 dB At also added
p_start = 0
p_stop = 5
p_points = 2
p_list=np.linspace(p_start,p_stop,p_points)

#SBM Cavity Drive 
drive_f= 5900.50 #MHz (blue:5936.821 red:5864.344/5864.310)
drive_power=0 # dBm



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
smb2.write('POW:ALC OFF') #Turn Auto level control off

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


#set constant gate voltage
print 'sweeping gate'
sweep('Vg',4.0)   #V slowly sweeps the gate 
                #(takes conversion into account)
qt.msleep(2)

#set sweep
pna.set_power(p_start)
pna.set_sweeppoints(points)
pna.set_resolution_bandwidth(bw)
pna.get_all() #get all the settings and store it in the settingsfile.
#get ready
pna.w("SENS:AVER:CLE") #clear prev averages
sweep_time = float(pna.q("SENS1:SWE:TIME?"))

print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
print 'averages of the pna: '+str(pna.get_averages())
print 'sweeptime per trace (sec): '+str(sweep_time)
print 'measurement loop:'


sweep_time = float(pna.q("SENS1:SWE:TIME?"))
time_axis=time_dummy*sweep_time*1000 # time axis in msec


########################
spyview_process(data,
                len(time_axis),
                0,
                time_axis[len(time_axis)-1],
                len(freq_list),
                (f_stop-freq)/1e9,
                (f_start-freq)/1e9,
                len(p_list),
                p_start,
                p_stop)
############################


for p in p_list:
    pna.set_power(p)
    print p
    p_dummy=np.linspace(p,p,points)
    for f in freq_list:
        print f
        freq_dummy=np.linspace(f,f,points)
        pna.w('SENS:FREQ '+str(f))
        pna.w("SENS:AVER:CLE")
        qt.msleep(wait_time)#avg*sweep_time)
        trace= pna.fetch_data(polar=True)
        trace2= pna.fetch_data(polar=False)
        data.add_data_point(p_dummy,(freq_dummy-freq),time_axis,trace[0],trace[1],trace2[0],trace2[1])
        data.new_block()

#sweep('Vg',0) #returns gate back to zero
data.close_file()
qt.mend()
