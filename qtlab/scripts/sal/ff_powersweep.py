#prepare environment
import qt
import visa
import numpy as np
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen.py')

    
#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "installed instruments: "+" ".join(instlist)
#install the drivers no check

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#if 'adwin' not in instlist:
  #  adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

if 'ff' not in instlist:
    ff=visa.instrument('TCPIP0::192.168.1.151::inst0::INSTR')

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
#med.set_device('ShunDevice')
#med.set_setup('BF_4, conversion is 1uA/V')
#med.set_user('Shun')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'EOS8_C_FF'
data = qt.Data(name=filename)
data.add_coordinate('Probe Frequency [MHz]')
data.add_coordinate('Voltage [uA]')
data.add_value('S21 [abs]')
data.add_value('S21 [rad]')

#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Sal\\EOS8_C\\temp_powersweep')
data.copy_file('FF_powersweep.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature
# 18mK
## 10dB on VNA out
## miteq on the input port 2
## I to V conversion 100uA/1Volt
##



######### Variables for NA
pinit=-45
bw=30
f_start=5.272*GHz
f_stop=5.372*GHz
f_pts=401
##hanger_f0=5900.59*MHz
##hanger_span=1000*kHz
##f1_start=hanger_f0-hanger_span/2
##f1_stop=hanger_f0+hanger_span/2

### Variables for field
#v_start=0
#v_stop=1.5
#v_pts=1501

### Variables for power
p_start = -45
p_stop =0
p_pts =10


### Preparing NA
ff.write('INST:SEL "NA";*OPC?')
ff.write('FREQ:STOP '+str(f_stop)+'\n')
ff.write('FREQ:STAR '+str (f_start)+'\n')
ff.write('BWID '+str(bw)+'\n')
ff.write('SOUR:POW '+str(pinit)+'\n')
ff.write('SWE:POIN '+str(f_pts)+'\n')
ff.write('CALC:PAR:DEF S21 \r')


### Prepare ADWIN for current sweep
#adwin.start_process()

########### making lists of values to be measured ###########
f_list=np.linspace(f_start,f_stop,f_pts)
#v_list=np.linspace(v_start,v_stop,v_pts)
p_list = np.linspace(p_start,p_stop,p_pts)
##################################################

qt.msleep(0.1)

for p in p_list:
    print 'current power '+str(p)+' power'
    ff.write('SOUR:POW ' +str(p)+'\n')
    print ff.ask('SOUR:POW?')
   #adwin.set_DAC_2(v)
    qt.msleep(2)
    #setting tarce 1
    ff.write('INIT \r')
    qt.msleep(15)
    ff.write('CALC:FORM MLOG \r')
    qt.msleep(2)
    trace_mlog = eval(ff.ask('CALC:DATA:FDAT? \r'))
    qt.msleep(2)
    ff.write('CALC:FORM PHAS \r')
    qt.msleep(2)
    trace_phase = eval(ff.ask('CALC:DATA:FDAT? \r'))
   
    v_dummy=np.linspace(p,p,len(f_list))
    data.add_data_point(v_dummy,f_list,trace_mlog, np.gradient(np.unwrap(np.deg2rad(trace_phase),np.pi)))
    data.new_block()
    spyview_process(data,f_start,f_stop,p)
    qt.msleep(0.01)
data.close_file()
qt.mend()
