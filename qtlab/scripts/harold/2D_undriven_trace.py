import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

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

#convert trace (list of amplitudes) to data, (frequency, amplitude) pairs:
start_frequency=275 #MHz
stop_frequency=325 #MHz
sweeppoints=101
bandwidth = 0.00001 #MHz

fsl.set_start_frequency(start_frequency)
fsl.set_stop_frequency(stop_frequency)
fsl.set_sweeppoints(sweeppoints)
fsl.set_resolution_bandwidth(bandwidth) #MHz

span=fsl.get_span()

fstep=span/(sweeppoints-1.0)
flist=np.arange(start_frequency,stop_frequency+fstep,fstep)

#set y variable
coordinate_names = {'vgate':'Gate voltage (V)','Vdd':'Vdd (V)'}
yvarname = 'vgate' # 'vgate' or 'Vdd'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 2.5
y_stop = 4.5
y_step = 0.1
Noysteps = (y_stop-y_start)/y_step + 1

#set fixed values
if yvarname != 'vgate':
    vgate_fixed = 3.5 #V
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if yvarname != 'Vdd':
    Vdd_fixed = 1 #V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed


#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()


#ready the fsl
fsl.set_trace_continuous(True)
fsl.set_filter_type('FFT')
fsl.set_trace_mode('AVER')
fsl.set_number_of_sweeps(10000)




#initialize spyview meta.txt file
spyview_process(reset=True)


queryingtime = 0.1
NoAverages = 2

#if fsl.get_sweeptime() > settlingtime:
#    settlingtime=fsl.get_sweeptime()*1.5
#    print 'settling time has been changed to sweeptime: %s' % settlingtime
#print 'settling time: %s, sweeptime: %s' % (settlingtime, fsl.get_sweeptime())

#Set up datafile
filename='lg-04xx31b2_2D_undriven_vs_'+yvarname

data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_value('Magnitude [dBm]')

data.create_file()
data.copy_file('2D_undriven_trace.py')




for yvar in linspace(y_start,y_stop,Noysteps):
    #set y variable
    if yvarname == 'vgate':
        ramp(vi,'vgate',yvar,sweepstep,sweeptime)
    elif yvarname == 'Vdd':
        ramp(vi,'vdd',yvar,sweepstep,sweeptime)
        
    print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
    y_array = yvar*ones(sweeppoints)

    fsl.initiate()
    
    currentsweepnumber=0

    while currentsweepnumber <= NoAverages:
        qt.msleep(queryingtime)
        currentsweepnumber =fsl.get_current_sweep_number() 
        

        
    trace=fsl.grab_trace() #actual measurement
    out=[flist,trace]
    data.add_data_point(out[0],y_array,out[1])

    data.new_block()
    spyview_process(data,start_frequency,stop_frequency,yvar)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=2)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')


#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vdd',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Vdd: %sV' % vi.get_vdd()

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring


data.close_file()

qt.mend()
