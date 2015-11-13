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
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

if 'smb' not in instlist:
    smb = qt.instruments.create('smb100a','RS_SMB100A', address='TCPIP::192.168.1.25::INSTR')

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#measurement information stored in manual in MED instrument
med.set_device('uglyDrum')
med.set_setup('BF')
med.set_user('Vibhor')

qt.mstart()
spyview_process(reset=True) #clear old meta-settings

filename = 'pnaDrive_withFixgate_cavityFreq_drive'
data = qt.Data(name=filename)
data.add_coordinate('Cavity freq [MHz]')
data.add_coordinate('Frequency (Hz)')
data.add_value('S21 [abs]')
data.add_value('S21 [to be checked Phase]')
data.add_value('S21 X')
data.add_value('S21 Y')
data.create_file()
data.copy_file('bf-PNA_trace_withFixgate_cavityFreq_drive.py')

kHz = 1e3
MHz = 1e6
GHz = 1e9

####Settings:
#Current temperature
# Gate = 1
#14 mK

## Power sweep close to red sideband and lowest power of the drum
## SETTINGS ARE Cavity driven at 5930.095 plus minus 39.4 MHZ
## VNA probe has 50 dB extra + 2 splitt arms
## Vari att HAS 3+4+5 SETTINs with 19dBm at source and one split arm


## VNA probe settings (VNA HAS different units carefullllll )
pow_start=0
f1_pts = 401
f1_bw = 100 #HZ

hanger_f0=39.4*MHz
hanger_span=400*kHz
f1_start = hanger_f0-hanger_span/2
f1_stop = hanger_f0+hanger_span/2

## Drum drive parameters
#drum_drive = -14
drum_freq=39.4

#### Preparing Drum drive
#smb.set_RF_frequency(drum_freq)
#smb.set_RF_power(drum_drive)
#smb.set_RF_state(True)


## Cavity drive settings
hang_st=5930.095-drum_freq-0.4  #MHz
hang_sp=5930.095-drum_freq+0.4 #MHz
hang_pt=101
hang_pow=19  # dBm


### Gate settings
#adwin.start_process()
#gate_start=1;
#gate_stop=1;
#gate_pt=1;
#adwin.set_DAC_2(gate_start)

## Preparing hanger
smb2.set_RF_frequency(hang_st)
smb2.set_RF_power(hang_pow)
smb2.set_RF_state(True)


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


########### making lists of values to be measured ###########

hang_f_list=np.linspace(hang_st,hang_sp,hang_pt)
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
gate_list=np.linspace(gate_start,gate_stop,gate_pt)

##################################################

pna.set_start_frequency(f1_start)
pna.set_stop_frequency(f1_stop)
qt.msleep(0.1)
sweep_time = float(pna.q("SENS1:SWE:TIME?"))
for hf in hang_f_list:
    print 'current freq '+str(hf)+' MHz'
    smb2.set_RF_frequency(hf)
    
    qt.msleep(1)
    pna.sweep()
    a=0
    while a==0:
        qt.msleep(3)
        try:
            a=eval(pna.q('*OPC?;'))
            break
        except(KeyboardInterrupt, SystemExit):
            raise
        except:
            a=0
    #qt.msleep(sweep_time+)
    trace1= pna.fetch_data(polar=True)
    trace2= pna.fetch_data(polar=False)
    hf_dummy=np.linspace(hf,hf,len(f_list))
    data.add_data_point(hf_dummy,f_list,trace1[0],trace1[1],trace2[0],trace2[1])
    data.new_block()
    spyview_process(data,f1_start,f1_stop,hf)
    qt.msleep(0.01)
data.close_file()
#adwin.set_DAC_2(0)
qt.mend()




