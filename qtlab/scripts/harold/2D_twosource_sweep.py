import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

begintime = time() #for measurement time calculation
recorddc=True #also record dc current?
forwardandreverse=False
highfrequency = True
returntozero = True
scalarsubtractbackground = True

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
    vi.add_variable_scaled('vbias',lockin,'out2',10,0.0)
    vi.add_variable_scaled('vdd',lockin,'out3',1,0.0)

if ('vm' not in instlist) and recorddc:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

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
current_gain = 0.001 #GV/A=mV/pA
#med.set_current_gain(current_gain)

#set frequencies
RF_start=250.0 #MHz
RF_stop=400.0 #MHz
RF_step=0.1 #MHz
NoRFsteps = (RF_stop-RF_start)/RF_step + 1

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2

#set y variable
coordinate_names = {'vgate':'Gate voltage (V)','RF_power':'RF power (dBm)','RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','f_Delta':'Deviation frequency (kHz)','Vdd':'Vdd (V)'}
yvarname = 'f_LO' # 'vgate' or 'RF_power' or 'f_LO' or 'f_Delta' or 'Vdd'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 997
y_stop = 40997
y_step = 20000
Noysteps = int((y_stop-y_start)/y_step + 1)

#set fixed values
#vbias_fixed=0.001 #V
if yvarname != 'vgate':
    vgate_fixed = 3.5 #V
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if yvarname != 'RF_power':
    RF_power=0 #dBm (Currently with 20dB in attenuation)   
    smb.set_RF_power(RF_power)
    print '+++ RF power: %sdBm +++' % RF_power

if yvarname != 'RFgate_power':
    RFgate_power=10 #dBm (Currently with 20dB in attenuation)   
    smbgate.set_RF_power(RFgate_power)
    print '+++ RF gate power: %sdBm +++' % RFgate_power

if yvarname != 'f_LO':
    LO_frequency= 9997.0 #997.0 #kHz
    print '+++ LO frequency: %skHz +++' % LO_frequency

if yvarname != 'Vdd':
    Vdd_fixed = 1 #V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

#set gate voltage to measure background signal
if scalarsubtractbackground:
    vgate_ref = 0 #V

#set filename
if highfrequency:
    filename='lg-04xx31b2_2D_HF_twosource_vs_'+yvarname
else:
    filename='lg-04xx31b2_2D_twosource_vs_'+yvarname
    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the high-frequency lockin
if highfrequency:
    HFlockin.set_reference('Signal Input 2')
    #HFlockin.set_reference('Internal')
    #HFlockin.set_frequency0(1000*LO_frequency) #kHz
    
    HFlockin.set_input_range0(0.02) #V
    HFlockin.set_input_range1(0.3) #V
    timeconstant = 0.01 #s
    HFlockin.set_timeconstant0(timeconstant)
    settlingtime = 0.01 #s used for wait time, should exceed 50 ms?
    HFlockin.set_impedance50Ohm0(True)
    HFlockin.set_external_clock(True)

#ready the smb
smb.set_RF_state(True)
smb.set_reference('EXT')
smbgate.set_RF_state(True)
smbgate.set_reference('INT')

smb.get_all()
smbgate.get_all()

if recorddc:
#ready vm
    vm.get_all()
    vm.set_trigger_continuous(False)

#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])

if scalarsubtractbackground & (yvarname != 'vgate'):
    data.add_value('R_subtracted (V)')
    data.add_value('R_ref (V)')

data.add_value('R (V)')
data.add_value('theta (rad)')
data.add_value('X (V)')
data.add_value('Y (V)')
data.add_value('DC (V)')

    
data.create_file()
data.copy_file('2D_twosource_sweep.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

ramp(vi,'vbias',0.001,sweepstep,sweeptime)

#Actual sweep
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
        smbgate.set_RF_frequency(RF_start)
        smb.set_RF_frequency(RF_start+LO_frequency/1000)
        qt.msleep(100*timeconstant)
    elif yvarname == 'Vdd':
        ramp(vi,'vdd',yvar,sweepstep,sweeptime)        
        
    qt.msleep(.2)

    #scalar subtraction of background (unavailable if gate voltage is looped)
    if scalarsubtractbackground & (yvarname != 'vgate'):
        x_ref=zeros(NoRFsteps)
        y_ref=zeros(NoRFsteps)
        r_ref=zeros(NoRFsteps)

        ramp(vi,'vgate',vgate_ref,sweepstep,sweeptime)
        print 'getting background reference trace'

        counter = 0
        for f in linspace(RF_start,RF_stop,NoRFsteps):
            smbgate.set_RF_frequency(f)
            smb.set_RF_frequency(f+LO_frequency/1000)
            qt.msleep(settlingtime)
                
            if highfrequency:
                x_ref[counter]=HFlockin.get_x()
                y_ref[counter]=HFlockin.get_y()
                r_ref[counter]=HFlockin.get_amplitude()
            else:
                rawdat=lockin.query('SNAP?1,2')
                datlist=rawdat.split(',')
                x_ref[counter]=1e12*float(datlist[0])
                y_ref[counter]=1e12*float(datlist[1])
                r_ref[counter]=sqrt((x_ref[counter])**2+(y_ref[counter])**2)

            counter=counter+1        
        ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
        
    if recorddc:
        i=vm.get_readval()/current_gain*-1e3
    else:
        i=0
        
    
    print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
    counter = 0
    for f in linspace(RF_start,RF_stop,NoRFsteps):
        smbgate.set_RF_frequency(f)
        smb.set_RF_frequency(f+LO_frequency/1000)
        qt.msleep(settlingtime)


        #take measurement    
        if highfrequency:
            x=HFlockin.get_x()
            y=HFlockin.get_y()
            r=HFlockin.get_amplitude()
            theta = HFlockin.get_phase()
        else:
            rawdat=lockin.query('SNAP?1,2')
            datlist=rawdat.split(',')
            x=1e12*float(datlist[0])
            y=1e12*float(datlist[1])
            r=sqrt(x**2+y**2)
            theta=arctan(y/x)

        #save data
        if scalarsubtractbackground & (yvarname != 'vgate'):
            r_subtracted = r-r_ref[counter]
            data.add_data_point(f,yvar,r_subtracted,r_ref[counter],r,theta,x,y,i)
        else:    
            data.add_data_point(f,yvar,r,theta,x,y,i)

        if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
            print 'RF frequency: %sMHz' % f
        counter=counter+1

    data.new_block()
    spyview_process(data,RF_start,RF_stop,yvar)

    if forwardandreverse:
        counter = 0
        for f in linspace(RF_stop,RF_start,NoRFsteps):
            smbgate.set_RF_frequency(f)
            smb.set_RF_frequency(f+LO_frequency/1000)

            if highfrequency:
                x=HFlockin.get_x()
                y=HFlockin.get_y()
                r=HFlockin.get_amplitude()
                theta = HFlockin.get_phase()
            else:
                rawdat=lockin.query('SNAP?1,2')
                datlist=rawdat.split(',')
                x=1e12*float(datlist[0])
                y=1e12*float(datlist[1])
                r=sqrt(x**2+y**2)
                theta=arctan(y/x)

            if scalarsubtractbackground & (yvarname != 'vgate'):
                r_subtracted = r-r_ref[counter]
                data.add_data_point(f,yvar,r_subtracted,r_ref[counter],r,theta,x,y,i)
            else:    
                data.add_data_point(f,yvar,r,theta,x,y,i)

            if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                print 'RF frequency: %sMHz' % f
            counter=counter+1

        data.new_block()
    
        spyview_process(data,RF_start,RF_stop,yvar)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=2)
plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')

if recorddc:
    plot2dc = qt.Plot2D(data, name='dccomp', coorddim=0, valdim=4)
    plot3Dc = qt.Plot3D(data, name='dc3d', coorddims=(0,1), valdim=4)
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
smbgate.set_RF_state(False)

if recorddc:
    vm.set_trigger_continuous(True)

data.close_file()

qt.mend()
