import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen3D.py')

begintime = time() #for measurement time calculation
returntozero = True
readoutdevice = 'zvb' #choose 'fsl' or 'zvb'
recorddc=True #also record dc current?
log_xscale = True #logarithmic x scale?

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsl' not in instlist:
    fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')

if 'zvb' not in instlist:
    zvb = qt.instruments.create('zvb','RS_ZVB',address='GPIB::21::INSTR')

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
    ivvi.set_dac_range(3,10000) #uses altered Optodac.py
    
if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
    vi.add_variable_scaled('vdd',ivvi,'dac6',1000,0.0)

if ('vm' not in instlist):
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')
    #smb = qt.instruments.create('smb','RS_SMB100A',address='TCPIP::169.254.247.179')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

#measurement information
med.set_temperature(3)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
#med.set_current_gain(current_gain)

#convert trace (list of amplitudes) to data, (frequency, amplitude) pairs:
start_frequency=0.3 #MHz
stop_frequency=4000 #MHz
sweeppoints=101
bandwidth = 0.01 #MHz
span = stop_frequency-start_frequency
fstep=span/(sweeppoints-1.0)
if log_xscale:
    f_array=logspace(log10(start_frequency),log10(stop_frequency),sweeppoints)
else:
    f_array=linspace(start_frequency,stop_frequency,sweeppoints)

if readoutdevice == 'fsl':
    fsl.set_start_frequency(start_frequency)
    fsl.set_stop_frequency(stop_frequency)
    fsl.set_sweeppoints(sweeppoints)
    fsl.set_resolution_bandwidth(bandwidth) #MHz
elif readoutdevice == 'zvb':
    zvb.set_start_frequency(start_frequency)
    zvb.set_stop_frequency(stop_frequency)
    zvb.set_sweeppoints(sweeppoints)
    zvb.set_resolution_bandwidth(bandwidth) #MHz    

if recorddc:
    vm.get_all()
    vm.set_trigger_continuous(False)
    
#set y variable
coordinate_names = {'vgate':'Gate voltage (V)','Vdd':'Vdd (V)','nothing':'Nothing'}
yvarname = 'vgate' # 'vgate' or 'Vdd'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 2.5
y_stop = 4.5
y_step = 2
if yvarname == 'nothing':
    Noysteps=1
    y_start =1
    y_stop=y_start+Noysteps-1
else:
    Noysteps = int(abs(y_stop-y_start)/y_step + 1)

#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = 0.507
z_stop = 2.507
z_step = 0.500
if zvarname == 'nothing':
    Nozsteps=1
    z_start =1
    z_stop=z_start+Nozsteps-1
else:
    Nozsteps = abs(int((z_stop-z_start)/z_step) + 1)

#set fixed values
#vbias_fixed=0.001 #V
if (yvarname != 'vgate') & (zvarname != 'vgate'):
    vgate_fixed = 0 #V
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if (yvarname != 'RF_power') & (zvarname != 'RF_power'):
    if readoutdevice == 'zvb':
        RF_power=-7 #dBm (Currently with 20dB in attenuation + 3dB from splitter)   
        zvb.set_source_power(RF_power)
        print '+++ RF power: %sdBm +++' % RF_power

if (yvarname != 'Vdd') & (zvarname != 'Vdd'):
    Vdd_fixed = 1 #V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)


    


#ready the lockin
lockin.get_all()
vi.get_vgate()

if readoutdevice == 'fsl':
    #ready the fsl
    fsl.set_trace_continuous(True)
    fsl.set_filter_type('FFT')
    fsl.set_trace_mode('AVER')
    fsl.set_number_of_sweeps(10000)
    queryingtime = 0.1 # don't use lower because has not "settled"
elif readoutdevice == 'zvb':
    zvb.set_trace_continuous(True)  
    zvb.set_averages(NoAverages)
    waittime=zvb.get_sweeptime()*NoAverages
    zvb.set_RF_state(True)

NoAverages = 2

#initialize spyview meta.txt file
spyview_process(reset=True)

qt.mstart()

#Set up datafile
if readoutdevice == 'fsl':
    filename='lg-04xx31b2_3D_undriven_spectrum_vs_'+yvarname+'_and_'+zvarname
elif readoutdevice == 'zvb':
    filename='lg-04xx31b2_3D_S21_vs_'+yvarname+'_and_'+zvarname

data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])
if readoutdevice == 'fsl':
    data.add_value('Magnitude (dBm)')
elif readoutdevice == 'zvb':    
    data.add_value('S21 (dB)')
data.add_value('Current (pA)')

data.create_file()
data.copy_file('3D_trace.py')


for zvar in linspace(z_start,z_stop,Nozsteps):


    #set z variable
    if zvarname == 'vgate':
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'RF_power':
        zvb.set_source_power(zvar)
    elif zvarname == 'Vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)

    z_array = zvar*ones(sweeppoints)
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    

    for yvar in linspace(y_start,y_stop,Noysteps):
        #set y variable
        if yvarname == 'vgate':
            ramp(vi,'vgate',yvar,sweepstep,sweeptime)
        elif zvarname == 'RF_power':
            zvb.set_source_power(zvar)
        elif yvarname == 'Vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)
            
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
        y_array = yvar*ones(sweeppoints)

        if readoutdevice=='fsl':
            fsl.initiate()
            currentsweepnumber=0

            while currentsweepnumber <= NoAverages:
                qt.msleep(queryingtime)
                currentsweepnumber =fsl.get_current_sweep_number() 
                
            trace=fsl.grab_trace() #actual measurement
        elif readoutdevice == 'zvb':
            zvb.set_start_frequency(start_frequency)
            zvb.set_stop_frequency(stop_frequency)
            qt.msleep(waittime)
            trace = zvb.grab_trace()

        #measure dc current    
        if recorddc:
            i=vm.get_readval()/current_gain*-1e3
        else:
            i=0
        i_array = i*ones(sweeppoints)

        data.add_data_point(f_array,y_array,z_array,trace,i_array)
        data.new_block()
        spyview_process(data,start_frequency,stop_frequency,y_start,y_stop,zvar)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)

if log_xscale:
    plot2dx.set_xlog(True)
    plot3Dx.set_xlog(True)
else:    
    plot2dx.set_xlog(False)
    plot3Dx.set_xlog(False)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')


#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)
    ramp(vi,'vdd',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Bias voltage: %sV' % vi.get_vbias()
print 'Vdd: %sV' % vi.get_vdd()

if recorddc:
    vm.set_trigger_continuous(True)

if readoutdevice=='zvb':
    zvb.set_RF_state(False)

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring


data.close_file()

qt.mend()
