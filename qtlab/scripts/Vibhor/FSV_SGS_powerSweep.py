import qt
import numpy
import visa
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')


instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136::inst0::INSTR')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_100A',address='TCPIP0::192.168.1.131::inst0::INSTR')

if 'sgs' not in instlist:
    sgs=qt.instruments.create('sgs','RS_SGS100A',address='TCPIP0::169.254.112.26::inst0::INSTR')
    
if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#Check and load instrument plugins


instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('Dynamic Range cavity')
med.set_setup('BF')
med.set_user('Vibhor')
## FSV details


####### Power details
pow_start=-20
pow_stop=10
pow_pts=31
f_sgs=5900.585

print fsv.query('*IDN?')
fsv_center_frequency=f_sgs # Unit is MHZ here
fsv_span= 100*1e-6 #MHz Wait time may have to adjusted if this number is changed
fsv_sweep_points = 501
fsv_BW=0.001e-3  #1 KHz

#fsv.reset()
fsv.set_center_frequency(fsv_center_frequency)
fsv.set_span(fsv_span)
fsv.set_resolution_bandwidth(fsv_BW)
fsv.set_sweeppoints(fsv_sweep_points)

# Setting up SMB
sgs.set_RF_power(pow_start)
sgs.set_RF_frequency(f_sgs)
sgs.set_RF_state(1)

qt.msleep(1)


################################
#      DATA INITIALIZATION
################################

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'Noise_Cal_800mK'
data = qt.Data(name=filename)
data.add_coordinate('power',size=pow_pts)
data.add_coordinate('fsv freq',size=fsv_sweep_points)
data.add_value('spectrum')

base_path = 'D:\\data\\Vibhor\\NeatDrumPostReview\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('FSV_SGS_powerSweep.py')

########################################
###         MEASUREMENT LOOP
########################################

#variables

pow_list=np.linspace(pow_start,pow_stop,pow_pts)
fsv_start=float(fsv_center_frequency)-float(fsv_span/2)
fsv_stop=float(fsv_center_frequency)+float(fsv_span/2)
fsv_list=np.linspace(fsv_start,fsv_stop,fsv_sweep_points)

print 'Start Experiments'

waittime=fsv.get_sweeptime()


for pw in pow_list:
    sgs.set_RF_power(pw)
    pw_dummy=list(pw*ones(fsv_sweep_points))
    qt.msleep(1)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current power '+ str(pw)
    qt.msleep(waittime+3)
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(pw_dummy,fsv_list,tr)
    spyview_process(data,fsv_start,fsv_stop,pw)
data.close_file()
qt.mend()
#end
