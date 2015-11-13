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

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
    ivvi.set_dac_range(3,10000) #uses altered Optodac.py

if False | ('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vattplus',ivvi,'dac2',1,0.0)
    vi.add_variable_scaled('vattctrl',ivvi,'dac3',1,0.0)

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')

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
RF_start=50 #MHz
RF_stop=750 #MHz
RF_step=100#0.05#MHz
NoRFsteps= (RF_stop-RF_start)/RF_step+1

#set readout frequencies
startfrequency = RF_start
stopfrequency=RF_stop

#how many prints on screen per loop
if ((RF_stop-RF_start)/RF_step+1) > 10:
    NoPrints = 10
else:
    NoPrints = 2

coordinate_names = {'vgate':'Gate voltage (V)','RF_power':'RF power (V)','RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','Vdd':'Vdd (V)','nothing':'Nothing'}
#set y variable
yvarname = 'f_LO' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 0.009
y_stop = 1000
y_step = 0.1
Noysteps = int((y_stop-y_start)/y_step + 1)


#set z variable
zvarname = 'vgate' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = -8.5
z_stop = 8.5
z_step = 0.1
if zvarname == 'nothing':
    z_stop=z_start
    Nozsteps=1
else:
    Nozsteps = abs(int((z_stop-z_start)/z_step) + 1)

#set fixed values
#vbias_fixed=0.001 #V
if (yvarname != 'RF_power') & (zvarname != 'RF_power'):
    RF_power=0 #dBm (Currently with 20dB in attenuation)   
    smb.set_RF_power(RF_power)
    print '+++ RF power: %sdBm +++' % RF_power

if (yvarname != 'RFgate_power') & (zvarname != 'RFgate_power'):
    RF_gate_power=0 #dBm (Currently with 10dB in attenuation)   
    smbgate.set_RF_power(RF_gate_power)
    print '+++ RF gate power: %sdBm +++' % RF_gate_power

if (yvarname != 'f_LO') & (zvarname != 'f_LO'):
    LO_frequency= 1000 #kHz
    print '+++ LO frequency: %skHz +++' % LO_frequency

if (yvarname != 'Vdd') & (zvarname != 'Vdd'):
    Vdd_fixed = 1 #V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)
filename='lg-04xx31b2_3D_twosource_collapsedtrace_vs_'+yvarname+'_and_'+zvarname
    


#ready the lockin
lockin.get_all()

#ready the smb
smb.set_RF_state(True)
smb.set_reference('EXT')
smb.get_all()

smbgate.set_RF_state(True)
smbgate.set_reference('INT')
smbgate.get_all()

#ready the fsl
fsl.set_trace_continuous(True)
fsl.set_filter_type('FFT') #use 'NORM' above 30 kHz
fsl.set_trace_mode('AVER')
fsl.set_number_of_sweeps(30000)
bandwidth = 0.0011 # MHz
fsl.set_resolution_bandwidth(bandwidth) #MHz

queryingtime = 0.1
NoAverages = 10

span = 0.2*bandwidth # MHz
fsl.set_span(span)

sweeppoints=101
fsl.set_sweeppoints(sweeppoints)

fstep=span/(sweeppoints-1.0)

#convert trace (list of amplitudes) to data, (frequency, amplitude) pairs:





#initialize spyview meta.txt file
spyview_process(reset=True)





#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('Drive frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])
data.add_value('Magnitude (dBm)')

data.create_file()
data.copy_file('3D_twosource_collapsedtrace.py')


#Actual sweep
qt.mstart()
smbgate.set_RF_frequency(RF_start)
smb.set_RF_frequency(RF_start+LO_frequency/1000)

for zvar in linspace(z_start,z_stop,Nozsteps):
    #set z variable
    if zvarname == 'vgate':
            ramp(vi,'vgate',zvar,sweepstep,sweeptime)
        elif zvarname == 'RF_power':
            smb.set_RF_power(zvar)
        elif zvarname == 'RFgate_power':
            smbgate.set_RF_power(zvar)
        elif zvarname == 'f_LO':
            LO_frequency=zvar
            HFlockin.set_frequency0(LO_frequency*1000)
        elif zvarname == 'tc':
            vartimeconstant=10**zvar
            HFlockin.set_timeconstant0(vartimeconstant)
            settlingtime = 10*vartimeconstant#s used for wait time, should exceed 50 ms?
        elif zvarname == 'Vdd':
            ramp(vi,'vdd',zvar,sweepstep,sweeptime)
    z_array=zvar*ones(NoRFsteps)
    
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    

    you were here
    
    for yvar in linspace(y_start,y_stop,Noysteps):
        #set y variable
        if yvarname == 'vgate':
            ramp(vi,'vgate',yvar,sweepstep,sweeptime)
        elif yvarname == 'RF_power':
            smb.set_RF_power(yvar)
        elif yvarname == 'RFgate_power':
            smbgate.set_RF_power(yvar)
        elif yvarname == 'f_LO':
            LO_frequency=yvar
            HFlockin.set_frequency0(LO_frequency*1000)
        elif yvarname == 'tc':
            vartimeconstant = 10**yvar
            HFlockin.set_timeconstant0(vartimeconstant)
            settlingtime = 10*vartimeconstant #s used for wait time, should exceed 50 ms?
        elif yvarname == 'Vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)        
        
        y_array=yvar*ones(NoRFsteps)
        
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
    
        counter = 0    
        for f in linspace(RF_start,RF_stop,NoRFsteps):
            smbgate.set_RF_frequency(f)
            
            fsl.set_center_frequency(f)
            qt.msleep(.02)
            fsl.initiate()
            currentsweepnumber=0
            while currentsweepnumber <= NoAverages:
                qt.msleep(queryingtime)
                currentsweepnumber =fsl.get_current_sweep_number() 

            trace=fsl.grab_trace() #actual measurement
            out = max(trace)
            data.add_data_point(f,yvar,zvar,out)

            if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                print 'RF frequency: %sMHz' % f
            counter=counter+1



        data.new_block()
        
    spyview_process(data,RF_start,RF_stop,y_start,y_stop,zvar)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')


#reset voltages
if returntozero:
    vi.set_vattplus(0)
    vi.set_vattctrl(0)
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
