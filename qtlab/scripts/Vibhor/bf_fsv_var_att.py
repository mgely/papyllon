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
    
if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#Check and load instrument plugins

## Configuring variable attenuator
    
var_att=visa.instrument('TCPIP0::192.168.1.113::INSTR')
print 'FOUND  '+ var_att.ask('*IDN?')
qt.msleep(1)
var_att.write('CONF:X AG8494')
var_att.write('CONF:Y AG8496')

##

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('Ugly drum')
med.set_setup('BF')
med.set_user('Vibhor')

##VARIABLE ATT setup

att_start=41
att_stop=0
att_points=42

##var_att.write('ATT:Y 10')
## FSV details
print fsv.query('*IDN?')
fsv_center_frequency=5930.14-41.2776 # Unit is MHZ here
fsv_span= 25 #MHz Wait tim emay have to adjusted if this number is changed
fsv_sweep_points = 1001
fsv_BW=0.00001  #10KHz

#fsv.reset()
fsv.set_center_frequency(fsv_center_frequency)
fsv.set_span(fsv_span)
fsv.set_resolution_bandwidth(fsv_BW)
fsv.set_sweeppoints(fsv_sweep_points)

# THIS TIME IS FOR THE tracking generator to learn the list
qt.msleep(3)


################################
#      DATA INITIALIZATION
################################

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'bf_fsv_var_att'
data = qt.Data(name=filename)
data.add_coordinate('Att',size=att_points)
data.add_coordinate('fsv freq',size=fsv_sweep_points)
data.add_value('spectrum')
data.add_value('AttX')
data.add_value('AttY')

data.create_file()
data.copy_file('bf_fsv_var_att.py')

#print 'prepare 2D plot'
#plot=qt.Plot2D(data, name=filename, coorddim=0, valdim=2) #buggy


########################################
###         MEASUREMENT LOOP
########################################

#variables

att_list=np.linspace(att_start,att_stop,att_points)
fsv_start=float(fsv_center_frequency)-float(fsv_span)
fsv_stop=float(fsv_center_frequency)+float(fsv_span)
fsv_list=np.linspace(fsv_start,fsv_stop,fsv_sweep_points)

print 'Start Experiments'

waittime=fsv.get_sweeptime()


for att in att_list:
    att_dummy=list(att*ones(fsv_sweep_points))
    attSP=divmod(att,10)
    var_att.write('ATT:X '+str(attSP[1]))
    var_att.write('ATT:Y '+str(attSP[0]*10))
    qt.msleep(1)
    fsv.write('INIT')
    fsv.write('INIT:CONT ON')
    print 'Current attenuation '+ str(att)
    qt.msleep(waittime+10)
    at1=eval(var_att.ask('ATT:Y?'))
    at0=eval(var_att.ask('ATT:X?'))
    att_dummy0=list(at0*ones(fsv_sweep_points))
    att_dummy1=list(at1*ones(fsv_sweep_points))
    fsv.write('INIT:CONT OFF')
    tr=fsv.get_trace()
    data.new_block()
    data.add_data_point(att_dummy,fsv_list,tr,att_dummy0,att_dummy1)
    spyview_process(data,fsv_start,fsv_stop,att)

data.close_file()
qt.mend()
#end
