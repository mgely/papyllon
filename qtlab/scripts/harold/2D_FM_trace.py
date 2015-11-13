import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

begintime = time() #for measurement time calculation
recorddc=False #also record dc current?
forwardandreverse=False
highfrequency = True
returntozero = True

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if highfrequency:
    if 'HFlockin' not in instlist:
        HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)
    
if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',lockin,'out1',1,0.0)
    vi.add_variable_scaled('vbias',lockin,'out2',100,0.0)
    vi.add_variable_scaled('vdd',lockin,'out3',1,0.0)

if ('vm' not in instlist) and recorddc:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')
    #smb = qt.instruments.create('smb','RS_SMB100A',address='TCPIP::169.254.247.179')

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
#med.set_current_gain(current_gain)

#set frequencies
RF_start=250 #MHz
RF_stop=400 #MHz
RF_step=0.01 #MHz

#set y variable
coordinate_names = {'vgate':'Gate voltage (V)','RF_power':'RF power (dBm)', 'f_LO':'LO frequency (kHz)','f_Delta':'Deviation frequency (kHz)','Vdd':'Vdd (V)'}
yvarname = 'vgate' # 'vgate' or 'RF_power' or 'f_LO' or 'f_Delta' or 'Vdd'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 3
y_stop = 4
y_step = 0.01

#set fixed values
#vbias_fixed=0.001 #V
if yvarname != 'vgate':
    vgate_fixed = 0 #V
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if yvarname != 'RF_power':
    RF_power=10 #dBm (Currently with 20dB in attenuation)   
    smb.set_RF_power(RF_power)
    print '+++ RF power: %sdBm +++' % RF_power

if yvarname != 'f_LO':
    FM_frequency= 99.987 #kHz
    smb.set_LF_frequency(FM_frequency)
    print '+++ LO frequency: %skHz +++' % FM_frequency

if yvarname != 'f_Delta':
    FM_deviation=500 #kHz
    smb.set_FM_deviation(FM_deviation)
    print '+++ Deviation frequency: %skHz +++' % FM_deviation

if yvarname != 'Vdd':
    Vdd_fixed = 1 #V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)


LF_voltage=1.0 #V (Low to minimize crosstalk to signal channel (yes, it's a problem))

if highfrequency:
    filename='lg-04xx31b2_2D_HF_FM_vs_'+yvarname
else:
    filename='lg-04xx31b2_2D_FM_vs_'+yvarname
    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the high-frequency lockin
if highfrequency:
    HFlockin.set_output_switch1(1) #0 = Signal Output 1, 1 = Signal Output 2
    HFlockin.set_power1(1) #V
    HFlockin.set_reference('Signal Input 2')
    HFlockin.set_input_range0(0.001) #V
    HFlockin.set_timeconstant0(0.3) #s

#ready the smb
smb.set_RF_state(False)
smb.set_RF_frequency(RF_start)
smb.set_LF_output_voltage(LF_voltage)
smb.set_LF_output_state(True)
smb.set_AM_state(False)
smb.set_FM_state(True)
smb.set_Modulation_state(True)
smb.set_RF_state(True)
smb.set_reference('EXT')

smb.get_all()

#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
if highfrequency:
    data.add_value('X (V)')
    data.add_value('Y (V)')
    data.add_value('DC (V)')
else:
    data.add_value('X (pA)')
    data.add_value('Y (pA)')
    data.add_value('DC (pA)')
    
data.create_file()
data.copy_file('2D_FM_trace.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep
lockin.get_X()
#ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
for yvar in arange(y_start,y_stop+y_step,y_step):
    #set y variable
    if yvarname == 'vgate':
        ramp(vi,'vgate',yvar,sweepstep,sweeptime)
    elif yvarname == 'RF_power':
        smb.set_RF_power(yvar)
    elif yvarname == 'f_LO':
        smb.set_LF_frequency(yvar)
    elif yvarname == 'f_Delta':
        smb.set_FM_deviation(yvar)
    elif yvarname == 'Vdd':
        ramp(vi,'vdd',yvar,sweepstep,sweeptime)        
        
    smb.set_RF_frequency(RF_start)
    qt.msleep(.2)
    print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
    counter = 0
    for f in arange(RF_start,RF_stop+RF_step,RF_step):
        smb.set_RF_frequency(f)
        qt.msleep(.05)
        if recorddc:
            dc=vm.read()
            dc*=-1e5
        else:
            dc=0
            
        if highfrequency:
            x=HFlockin.get_x()
            y=HFlockin.get_y()
        else:
            rawdat=lockin.query('SNAP?1,2')
            datlist=rawdat.split(',')
            x=1e12*float(datlist[0])
            y=1e12*float(datlist[1])
            
        data.add_data_point(f,yvar,x,y,dc)

        if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(10-1))==0:
            print 'RF frequency: %sMHz' % f
        counter=counter+1

    data.new_block()
    spyview_process(data,RF_start,RF_stop,yvar)

    if forwardandreverse:
        counter = 0
        for f in np.flipud(arange(RF_start,RF_stop+RF_step,RF_step)):
            smb.set_RF_frequency(f)
            qt.msleep(.05)
            if recorddc:
                dc=vm.read()
                dc*=-1e5
            else:
                dc=0

            if highfrequency:
                x=HFlockin.get_x()
                y=HFlockin.get_y()
            else:
                rawdat=lockin.query('SNAP?1,2')
                datlist=rawdat.split(',')
                x=1e12*float(datlist[0])
                y=1e12*float(datlist[1])

            data.add_data_point(f,yvar,x,y,dc)

            if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(10-1))==0:
                print 'RF frequency: %sMHz' % f
            counter=counter+1

        data.new_block()
    
        spyview_process(data,RF_start,RF_stop,yvar)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=2)
plot2dc = qt.Plot2D(data, name='dccomp', coorddim=0, valdim=4)
plot3Dc = qt.Plot3D(data, name='dc3d', coorddims=(0,1), valdim=4)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')
plot2dc.save_png(filepath=data.get_dir()+'\\'+'plot2dc.png')
plot3Dc.save_png(filepath=data.get_dir()+'\\'+'plot3Dc.png')

#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)
    if highfrequency:
        ramp(vi,'vdd',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Vdd: %sV' % vi.get_vdd()

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring

smb.set_RF_state(False)

data.close_file()

qt.mend()
