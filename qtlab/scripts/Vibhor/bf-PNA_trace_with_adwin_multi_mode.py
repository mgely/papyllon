#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('meta3d.py')
#execfile('metagen.py')

    
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
med.set_device('AnnealSample')
med.set_setup('He3')
med.set_user('Vibhor')

qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

filename = 'magDependance'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('mode')
data.add_coordinate('Field [V]')
data.add_value('S21 [abs]')
data.add_value('S21 [Phase]')
data.add_value('S21 [X]')
data.add_value('S21 [Y]')
#data.create_file()

base_path = 'D:\\data\\Vibhor\\AnnealedHangers\\'
now=localtime()
date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '___' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)
data.create_file(datadirs=base_path+date_path+'__'+filename)

data.copy_file('bf-PNA_trace_with_adwin_multi_mode.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
# Attenuation 60 dB on arm with blue cables 8 dB and 45 dB inside
## Two miteq + cold ampliers
## Shun's new magnet is installed with 10 mA giving 0.45 mT
## Adwin current conversion is 20 mA/V with Symm and I mode
## Rough resistance of the magnet cold is abt 500 Ohms with normal wire

pow_start=0
f1_pts = 801
f1_bw = 100 #HZ
hanger_f0=1000*MHz
hanger_span=25.0*MHz

f1_start= hanger_f0-hanger_span/2
f1_stop= hanger_f0+hanger_span/2



pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)


### Gate settings
#adwin.start_process()
gate_start=-0.75;
gate_stop=0.75;
gate_pt=301;

########### making lists of values to be measured ###########

#mode_list=[4540.12*MHz,4683.9*MHz,4836.0*MHz,4999.0*MHz,5173.0*MHz,5363.0*MHz,5558.0*MHz,5774.0*MHz,6006.6*MHz,6260.8*MHz]

mode_list=[4528.0*MHz,4669.0*MHz,4821.0*MHz,4981.0*MHz,5157.0*MHz,5353.0*MHz,5541.0*MHz,5753.0*MHz,5989.0*MHz,6241.0*MHz]
f_list=np.linspace(-1.0,1.0,f1_pts)

gate_list=np.linspace(gate_start,gate_stop,gate_pt)
#######################################################

''' setup the pna for an S21 measurement with given values '''
print 'Prepare PNA'
pna.reset_full() #proper reset command required to kill of bugs with the PNA
pna.setup(measurement_type='S21',start_frequency=f1_start,stop_frequency=f1_stop, sweeppoints=(f1_pts),bandwidth=f1_bw,level=pow_start)
pna.get_all() #get all the settings and store it in the settingsfile.
sweep_time = float(pna.q("SENS1:SWE:TIME?"))


####   EXPERIMENTAL AREA  ##########
print 'set experimental stuf, point averages, ...'
pna.set_averages_off()


##################################################

print 'measurement loop:'

pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))


########################
spyview_process(data,
                f1_pts,
                -1.0,
                1.0,
                10,
                10,
                1,
                gate_pt,
                gate_start,
                gate_stop)
############################


for gt in gate_list:
    adwin.set_DAC_2(gt)
    print 'Gate value ADWIN '+str(gt)+' Volt'
    qt.msleep(1)
    for mode in mode_list:
        pna.set_start_frequency(mode - hanger_span/2)
        pna.set_stop_frequency(mode + hanger_span/2)
        pna.sweep()
        trace= pna.fetch_data(polar=True)
        trace2= pna.fetch_data(polar=False)
        md_dummy=np.linspace(mode,mode,f1_pts)
        gt_dummy=np.linspace(gt,gt,f1_pts)
        data.add_data_point(gt_dummy,md_dummy,f_list,trace[0],trace[1],trace2[0],trace2[1])

        data.new_block()
    #spyview_process(data,-1,1,10,gt)
    qt.msleep(0.01)
data.close_file()
qt.mend()




