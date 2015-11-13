import visa
import numpy
execfile('metagen.py')


## LOG BOOK FoR no recordable parameters
## Driven at 32.741 KHz 5V
## AVG count to 500


##  VARIABLES

f_center=32.741e3;
f_span=200;
f_start=f_center-f_span/2
f_stop=f_center+f_span/2
numpt=1001
bandwidth=10;
sweep_points=1001

smb_start=2.5e3
smb_stop=5e3;
smb_nmpts=251;
smb_power=15;

## CREATE INstruments

ff=visa.instrument('TCPIP0::A-N9916A-01189::inst0::INSTR')
smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::30::INSTR')

## SETTING up SA
ff.write('*RST;*OPC?')
## segment to check that operation is over
while eval(ff.ask('*OPC?'))!=1:
    qt.msleep(1)
    print 'checking OPC 1'
ff.write('INST "SA";')
## segment to check that operation is over
while eval(ff.ask('*OPC?'))!=1:
    qt.msleep(1)
    print 'checking OPC 2'
ff.write('FREQ:CENT '+str(f_center))
## segment to check that operation is over
while eval(ff.ask('*OPC?'))!=1:
    qt.msleep(1)
    print 'checking OPC 3'
ff.write('FREQ:SPAN '+str(f_span))
## segment to check that operation is over
while eval(ff.ask('*OPC?'))!=1:
    qt.msleep(1)
    print 'checking OPC 4'
ff.write('BAND '+str(bandwidth))
## segment to check that operation is over
while eval(ff.ask('*OPC?'))!=1:
    qt.msleep(1)
    print 'checking OPC 5'
ff.write('SWE:POIN '+str(sweep_points))
## segment to check that operation is over
while eval(ff.ask('*OPC?'))!=1:
    qt.msleep(1)
    print 'checking OPC 6'
ff.write('AMPL:UNIT DBM')

## SETTING UP SMB

smb.set_RF_frequency(1e3)
smb.set_RF_power(smb_power)
smb.set_RF_state(1)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data
filename = 'tuningFork'
data = qt.Data(name=filename)
data.add_coordinate('smb frequency[MHz]')
data.add_coordinate('Frequency [Hz]',size=numpt)
data.add_value('RF measure [dBm]')

data.create_file()
data.copy_file('FFscript.py')

#print 'prepare 2D plot'
plot=qt.Plot2D(data, name=filename, coorddim=1, valdim=2) #buggy
smb_flist=np.linspace(smb_start,smb_stop,smb_nmpts)
ff_list=np.linspace(f_start,f_stop,numpt)
trace=[]
ff.write('INIT:CONT 0')
for i in smb_flist:
    smb.set_RF_frequency(i)
    ff.write('INIT;*OPC')
    ## segment to check that operation is over
    while eval(ff.ask('*OPC?'))!=1:
        qt.msleep(1)
        print 'checking OPC loop'
    qt.msleep(2)
    trace=eval(ff.ask('TRAC:DATA?'))
    data.new_block()
    dummy_smb_f=np.linspace(i,i,len(ff_list))
    data.add_data_point(dummy_smb_f,ff_list,trace) #store data
    spyview_process(data,f_start,f_stop,i) 
    qt.msleep(0.1) #wait 10 usec so save etc
data.close_file()
qt.mend()
ff.close()
#end
