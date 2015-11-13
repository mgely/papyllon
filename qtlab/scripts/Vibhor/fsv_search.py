import qt
import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136::inst0::INSTR')
    
if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('NeatDrum')
med.set_setup('BF,fsv')
med.set_user('Vibhor')

#print smb2.query('*IDN?')
print fsv.query('*IDN?')


fsv_center_frequency=10 # Unit is MHZ here
fsv_span= 1.0 #MHz Wait tim emay have to adjusted if this number is changed
fsv_sweep_points = 2001
fsv_BW=5e-5


#fsv.reset()
fsv.set_center_frequency(fsv_center_frequency)
fsv.set_span(fsv_span)
fsv.set_resolution_bandwidth(fsv_BW)
fsv.set_sweeppoints(fsv_sweep_points)
# center freq sweep
freq_start=2
freq_stop=100
freq_pt=99


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'fsv-search'
data = qt.Data(name=filename)
data.add_coordinate('span',size=fsv_sweep_points)
data.add_coordinate('fsv Center freq',size=freq_pt)
data.add_value('spectrum')

#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\neatDrum\\20140213')
data.copy_file('fsv_search.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables
flist=np.linspace(float(freq_start),float(freq_stop),freq_pt)

#fsv_list=np.linspace(fsv_start,fsv_stop,fsv_sweep_points)
fsv_list=np.linspace(-500,500,fsv_sweep_points)
print 'Start Experiments'

waittime=fsv.get_sweeptime()


for freq in flist:
    freq_dummy=list(freq*ones(fsv_sweep_points))
    fsv.set_center_frequency(freq)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current frequency ',freq
    qt.msleep(waittime+4.0)
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(freq_dummy,fsv_list,tr)
    spyview_process(data,-500,500,freq)

data.close_file()
qt.mend()
#end
