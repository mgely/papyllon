#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
#execfile('metagen3D_crazy.py')
execfile('metagen.py')

### Dispsesion of the mode
def dispersion(x):
    return 36.289-0.16382*x-2.4496*x*x

    
 
#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "installed instruments: "+" ".join(instlist)
#install the drivers no check

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#if 'pna' not in instlist:
#    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('NeatDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'DuffingSign'
data = qt.Data(name=filename)
data.add_coordinate('Gate [V]')
data.add_coordinate('Frequency (Hz)')
data.add_value('S21 [abs]')
data.add_value('S21 [rad]')
data.add_value('X')
data.add_value('Y')
base_path = 'D:\\data\\Vibhor\\neatDrum\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)
data.copy_file('Homodyne_Fwd_Rev_Follow_Gate.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature 13 mK
# Gate = sweep
#See logbook For measurement Scheme


### Gate settings
#adwin.start_process()
gate_start=1;
gate_stop=-1;
gate_pt=101;
gate_list=np.linspace(gate_start,gate_stop,gate_pt)
adwin.set_DAC_2(gate_start)
###
print 'sweeping gate to start'
qt.msleep(10)
pow_start=30
probe_pt =2001
bw = 1000 #HZ
probe_span=0.50*MHz


pna.set_power(pow_start)
pna.set_resolution_bandwidth(bw)


########### making lists of values to be measured ###########
f_list=np.linspace(-probe_span/2,probe_span/2,(2*probe_pt))
#######################################################

qt.msleep(0.1)

######################################

########## Print settings ################

print 'PNA power: '+str(pna.get_power()) +' dBm'
print 'bw: ' +str(pna.get_resolution_bandwidth()) +' Hz'


##################################################

print 'measurement loop:'


sweep_time = float(pna.q("SENS1:SWE:TIME?"))
for gt in gate_list:
    adwin.set_DAC_2(gt)
    print 'Gate value ADWIN '+str(gt)+' Volt'
    qt.msleep(2)
    probe_f0=((dispersion(gt)*1000)//1)*1000.0
    print 'Setting center at '+str(probe_f0/1000.0/1000.0)
    f1_start=probe_f0-probe_span/2
    f1_stop=probe_f0+probe_span/2
    pna.w('SENS:FOM:RANG:SEGM1:FREQ:STAR '+str(f1_start))
    pna.w('SENS:FOM:RANG:SEGM1:FREQ:STOP '+str(f1_stop))
    pna.w('SENS:FOM:RANG:SEGM1:SWE:POIN '+str(probe_pt))
    pna.w('SENS:FOM:RANG:SEGM2:FREQ:STAR '+str(f1_stop))
    pna.w('SENS:FOM:RANG:SEGM2:FREQ:STOP '+str(f1_start))
    pna.w('SENS:FOM:RANG:SEGM2:SWE:POIN '+str(probe_pt))
    pna.sweep()
    trace= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    gt_dummy=np.linspace(gt,gt,len(f_list))
    data.add_data_point(gt_dummy,f_list,trace[0],trace[1],trace2[0],trace2[1])
    data.new_block()
    spyview_process(data,-probe_span/2,probe_span/2,gt)
    qt.msleep(0.01)
data.close_file()
#adwin.set_DAC_2(0)
qt.mend()




