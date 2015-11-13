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

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)










#measurement information stored in manual in MED instrument
med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor,Marnix')










qt.mstart()
spyview_process(reset=True) #clear old meta-settings












filename = 'Cavity'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 [X]')
data.add_value('S21 [Y]')






base_path = 'D:\\data\\Marnix\\Cavity\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('bf-PNA_trace.py')









kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature 18 mK
# Gate = 0
#
# see logbook enterty 26-5-14 
# Sideband drive frequency 5936.905 MHz
# power = 30 dBm





#cavity response values
#pow_start=10
#f1_pts = 1001
#f1_bw = 6 #HZ
#hanger_f0=5900.5473*MHz # center frequency
#hanger_span=3*MHz # Span of measurement



#voor red side band measurement
pow_start=10
f1_pts = 501
f1_bw = 2 #HZ
hanger_f0=5900.5473*MHz # center frequency
hanger_span=150*kHz # Span of measurement






f1_start= hanger_f0-hanger_span/2
f1_stop= hanger_f0+hanger_span/2













########### making lists of values to be measured ###########
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))

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


pna.sweep()

trace= pna.fetch_data(polar=True)


trace2= pna.fetch_data(polar=False)


data.add_data_point(f_list,trace[0],trace[1],trace2[0],trace2[1])

#soms op -1 en 1 zetten
spyview_process(data,-1,1,1)
qt.msleep(0.01)
data.close_file()
qt.mend()
