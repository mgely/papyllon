import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen3D.py')

begintime = time() #for measurement time calculation
returntozero = True

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsl' not in instlist:
    fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')
    
if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',lockin,'out1',1,0.0)
    vi.add_variable_scaled('vbias',lockin,'out2',100,0.0)
    vi.add_variable_scaled('vdd',lockin,'out3',1,0.0)

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')
    #smb = qt.instruments.create('smb','RS_SMB100A',address='TCPIP::169.254.247.179')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
#med.set_current_gain(current_gain)

#set drive frequencies
RF_start=250 #MHz
RF_stop=400 #MHz
RF_step=10 #0.05#MHz

#set readout frequencies
startfrequency = RF_start
stopfrequency=RF_stop

#how many prints on screen per loop
if ((RF_stop-RF_start)/RF_step+1) > 10:
    NoPrints = 10
else:
    NoPrints = 2

#set gates
vg_start=3
vg_stop=4
vg_step=0.1

#set fixed values
RF_gate_power=10 #dBm (Currently with 20dB in attenuation)   
smbgate.set_RF_power(RF_gate_power)
print '+++ RF gate power: %sdBm +++' % RF_gate_power

Vdd_fixed = 1 #V
ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
print '+++ Vdd: %sV +++' % Vdd_fixed

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

filename='lg-04xx31b2_3D_directreadout_vs_gate'
    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the smb
smbgate.set_RF_state(True)
smbgate.set_reference('INT')
smbgate.get_all()

#ready the fsl
fsl.set_trace_continuous(True)
fsl.set_filter_type('FFT') #use 'NORM' above 30 kHz
fsl.set_trace_mode('AVER')
fsl.set_number_of_sweeps(30000)
bandwidth = 0.01 # MHz
fsl.set_resolution_bandwidth(bandwidth) #MHz

queryingtime = 0.1
NoAverages = 10

span = 10*bandwidth # MHz
fsl.set_span(span)

sweeppoints=101
fsl.set_sweeppoints(sweeppoints)

fstep=span/(sweeppoints-1.0)

#convert trace (list of amplitudes) to data, (frequency, amplitude) pairs:





#initialize spyview meta.txt file
spyview_process(reset=True)





#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)')
data.add_coordinate('Drive frequency (MHz)')
data.add_coordinate('Gate voltage (V)')
data.add_value('Magnitude [dBm]')

data.create_file()
data.copy_file('3D_directreadout_trace.py')


#Actual sweep
smb.set_RF_frequency(RF_start)
smbgate.set_RF_frequency(RF_start)

for vg in linspace(vg_start,vg_stop,(vg_stop-vg_start)/vg_step+1):
    ramp(vi,'vgate',vg,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vg
    vg_array = vg*ones(sweeppoints)

    counter = 0
    for f in arange(RF_start,RF_stop+RF_step,RF_step):
        smbgate.set_RF_frequency(f)
        f_array = f*ones(sweeppoints)

        fsl.set_center_frequency(f)
        fsl.initiate()
        qt.msleep(.2)
        currentsweepnumber=0

        flist=linspace(f-span/2,f+span/2,sweeppoints)

        while currentsweepnumber <= NoAverages:
            qt.msleep(queryingtime)
            currentsweepnumber =fsl.get_current_sweep_number() 

        trace=fsl.grab_trace() #actual measurement
        out=[flist,trace]
        data.add_data_point(out[0],f_array,vg_array,out[1])

        if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
            print 'RF frequency: %sMHz' % f
        counter=counter+1

        data.new_block()

    #data.new_block()
    spyview_process(data,start_frequency,stop_frequency,RF_start,RF_stop,vg)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=2)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')


#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vdd',0,sweepstep,sweeptime)

fsl.set_trace_continuous(True)#mend should do this, but...

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Vdd: %sV' % vi.get_vdd()

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring

smb.set_RF_state(False)
smbgate.set_RF_state(False)

data.close_file()

qt.mend()
