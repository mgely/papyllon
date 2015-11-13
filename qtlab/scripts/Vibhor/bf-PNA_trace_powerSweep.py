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

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::192.168.1.42::inst0::INSTR')

#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('MultiPlex')
med.set_setup('He3')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'S211_powerSweep_multi_'
data = qt.Data(name=filename)
data.add_coordinate('Power [dBm]')
data.add_coordinate('Frequency (Hz)')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')

base_path = 'D:\\data\\Vibhor\\He3Multiplex\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)


data.copy_file('bf-PNA_trace_powerSweep.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#300 mK
# 60 dB on Arm + 8 dB cable + 45 dB inside
## Cold Amp + Two Miteq

pow_start=-30
pow_stop=30
pow_pt=11

f1_pts = 501
f1_bw = 100 #HZ
hanger_f0=(4540.12)*MHz
hanger_span=2.5*MHz
f1_start=hanger_f0-hanger_span/2
f1_stop=hanger_f0+hanger_span/2

pna.set_power(pow_start)
pna.set_resolution_bandwidth(f1_bw)
pna.set_sweeppoints(f1_pts)
pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)


########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
pow_list=np.linspace(pow_start,pow_stop,pow_pt)
#######################################################

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

######################################

########## Print settings ################

print 'step size: '+str((f1_stop-f1_start)/(f1_pts-1)) +' Hz'
print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'
print 'averages of the pna: '+str(pna.get_averages())
print 'sweeptime per trace (sec): '+str(sweep_time)

##################################################

print 'measurement loop:'

pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)
qt.msleep(0.1)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
for pw in pow_list:
    pna.set_power(pw)
    if -30<=pw<-20:
        pna.set_resolution_bandwidth(5)
    elif -20<=pw<-15:
        pna.set_resolution_bandwidth(10)
    elif -15<=pw<-10:
        pna.set_resolution_bandwidth(20)
    elif -10<=pw-5:
        pna.set_resolution_bandwidth(30)
    elif -5<=pw<10:
        pna.set_resolution_bandwidth(50)
    elif 10<=pw<=30:
        pna.set_resolution_bandwidth(100)
    print 'Power NOW   '+str(pw)
    print 'Current BW '+str(pna.get_resolution_bandwidth())
    pna.sweep()
    trace= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    pw_dummy=np.linspace(pw,pw,len(f_list))
    data.add_data_point(pw_dummy,f_list,trace[0],trace[1],trace2[0],trace2[1]) #for S21 vs power
    data.new_block()
    spyview_process(data,f1_start,f1_stop,pw)
    qt.msleep(0.01)

data.close_file()
qt.mend()


execfile('bf_batch.py')
