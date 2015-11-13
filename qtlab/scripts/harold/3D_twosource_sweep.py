#fNEPBW / fcut-off = 2 * pi * K_NEPBW / (sqrt(2**(1/n) - 1)
#K_NEPBW = [1/4.0;1/8.0;3/32.0;5/64.0;35/512.0;63/1024.0;231/4096.0;429/8192.0
#page 659, 13.2:Signal bandwidth
import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen3D.py')

begintime = time() #for measurement time calculation
recorddc=False #also record dc current?
forwardandreverse=False #sweep forward and reverse?
highfrequency = False #measure with HFlockin (Zurich Instruments)?
returntozero = True #sweep voltages back to zero?
scalarsubtractbackground = False #subtract electrical mixing signal
measurecollapsedtrace = False #measure with R&S spectrum analyzer and record maximum?
measurenoise = False #set ch1&ch2 output manually to noise on SR830
displayintermediatetime=True

if measurecollapsedtrace | measurenoise:
    scalarsubtractbackground = False


#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if highfrequency:
    if 'HFlockin' not in instlist:
        HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
    ivvi.set_dac_range(3,10000) #uses altered Optodac.py

if not highfrequency:   
    if 'lockin' not in instlist:
        lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'fsl' not in instlist:
    fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')    

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
    vi.add_variable_scaled('vdd',ivvi,'dac6',1000,0.0)

if ('vm' not in instlist):
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if ('vm2' not in instlist):
    vm2 = qt.instruments.create('vm2','Keithley_2700',address='GPIB::16')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if False or ('smb' not in instlist):
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')
    #smb = qt.instruments.create('smb','RS_SMB100A',address='TCPIP::169.254.247.179')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
#med.set_current_gain(current_gain)

#set frequencies
RF_start=200 #MHz
RF_stop=250 #MHz
RF_step=50 #MHz
NoRFsteps = int((RF_stop-RF_start)/RF_step + 1)

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2

coordinate_names = {'vgate':'Gate voltage (V)','RF_power':'RF power (dBm)','RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','Vdd':'Vdd (V)','tc': 'Logarithm of time constant (log (s))', 'RF_phase':'RF phase (deg)','RFgate_phase':'RF gate phase (deg)','nothing':'Nothing'}
#set y variable
yvarname = 'f_LO' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 0.1
y_stop = 10
y_step = 0.1
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
    RF_power=3#-7 #dBm (Currently with 20dB in attenuation + 3dB from splitter)   
    smb.set_RF_power(RF_power)
    print '+++ RF power: %sdBm +++' % RF_power

if (yvarname != 'RFgate_power') & (zvarname != 'RFgate_power'):
    RFgate_power=3 #dBm (Currently with 10dB in attenuation + 3dB from splitter)   
    smbgate.set_RF_power(RFgate_power)
    print '+++ RF gate power: %sdBm +++' % RFgate_power

if (yvarname != 'f_LO') & (zvarname != 'f_LO'):
    LO_frequency= 0.507 #997.0 #kHz
    print '+++ LO frequency: %skHz +++' % LO_frequency

if (yvarname != 'tc') & (zvarname != 'tc'):
    if highfrequency:
        logtimeconstant = -2 #minimum: 780ns ~ 10**(-6.1)
        timeconstant_fixed = 10**logtimeconstant
        timeconstant=timeconstant_fixed
        HFlockin.set_timeconstant0(timeconstant_fixed) #timeconstant_fixed
        settlingtime = 10*timeconstant #10*timeconstant_fixed #s used for wait time, should exceed 50 ms?
    else:
        timeconstantformat = int(lockin.get_tau())
        logtimeconstant = timeconstantformat/2.0-5
        timeconstant_fixed = 10**logtimeconstant
        settlingtime = 10*timeconstant_fixed #s used for wait time, should exceed 50 ms?
    print '+++ timeconstant: %ss +++' % timeconstant_fixed

if (yvarname != 'Vdd') & (zvarname != 'Vdd'):
    Vdd_fixed = 1 #V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

if (yvarname != 'RF_phase') & (zvarname != 'RF_phase'):
    RF_phase=0 #deg 
    smb.set_RF_phase(RF_phase)
    print '+++ RF phase: %sdeg +++' % RF_phase

if (yvarname != 'RFgate_phase') & (zvarname != 'RFgate_phase'):
    RFgate_phase=0 #deg 
    smbgate.set_RF_phase(RFgate_phase)
    print '+++ RFgate phase: %sdeg +++' % RFgate_phase


#set gate voltage to measure background signal at
if scalarsubtractbackground:
    vgate_ref = 0 #V

#set filename
if measurecollapsedtrace:
    filename='lg-04xx31b2_2D_spectrum_twosource_vs_'+yvarname+'_and_'+zvarname
else:
    if highfrequency:
        filename='lg-04xx31b2_2D_HF_twosource_vs_'+yvarname+'_and_'+zvarname
    else:
        filename='lg-04xx31b2_2D_twosource_vs_'+yvarname+'_and_'+zvarname
    
qt.mstart()

#ready the lockin
if not highfrequency:   
    lockin.get_all()

#sensitivity setting for SR830 in amperes
sensitivity_map={ 
                0 : 2e-15 ,
                1 : 5e-15 ,
                2 : 10e-15 ,
                3 : 20e-15 ,
                4 : 50e-15 ,
                5 : 100e-15,
                6 : 200e-15 ,
                7 : 500e-15 ,
                8 : 1e-12 ,
                9 : 2e-12 ,
                10 : 5e-12 ,
                11 : 10e-12 ,
                12 : 20e-12 ,
                13 : 50e-12 ,
                14 : 100e-12 ,
                15 : 200e-12 ,
                16 : 500e-12 ,
                17 : 1e-9 ,
                18 : 2e-9 ,
                19 : 5e-9 ,
                20 : 10e-9 ,
                21 : 20e-9 ,
                22 : 50e-9 ,
                23 : 100e-9 ,
                24 : 200e-9 ,
                25 : 500e-9 ,
                26 : 1e-6
            }

#ready the high-frequency lockin
if highfrequency:
    HFlockin.set_reference('Signal Input 2')
    HFlockin.set_input_range0(0.03) #V
    HFlockin.set_input_range1(0.3) #V
    HFlockin.set_impedance50Ohm0(True)
    HFlockin.set_external_clock(True)

#ready the smb
smb.set_RF_state(True)
smb.set_reference('EXT')
smbgate.set_RF_state(True)
smbgate.set_reference('INT')

smb.get_all()
smbgate.get_all()

#ready the fsl
fsl.set_trace_continuous(True)
fsl.set_filter_type('FFT') #use 'NORM' above 30 kHz
fsl.set_trace_mode('AVER')
fsl.set_number_of_sweeps(30000)
bandwidth = 0.00011 # MHz
fsl.set_resolution_bandwidth(bandwidth) #MHz

queryingtime = 0.1 # don't use lower because has not "settled"
NoAverages = 2

span = 0.2*bandwidth # MHz
fsl.set_span(span)

sweeppoints=101
fsl.set_sweeppoints(sweeppoints)

fstep=span/(sweeppoints-1.0)

vm.get_all()
vm.set_trigger_continuous(False)
vm2.get_all()
vm2.set_trigger_continuous(False)

if recorddc:
#ready vm
    ramp(vi,'vbias',0.001,sweepstep,sweeptime)

#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('Drive frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])

if measurecollapsedtrace:
        data.add_value('Power (dBm)')
else:
    if scalarsubtractbackground & (yvarname != 'vgate'):
        data.add_value('R_subtracted (V)')
        data.add_value('R_ref (V)')
                        
    if highfrequency:
        data.add_value('R (V)')
        data.add_value('theta (rad)')
        data.add_value('X (V)')
        data.add_value('Y (V)')
        data.add_value('DC (pA)')
    else:
        data.add_value('R (pA)')
        data.add_value('theta (rad)')
        data.add_value('X (pA)')
        data.add_value('Y (pA)')
        data.add_value('DC (pA)')
        if measurenoise:
            data.add_value('X noise (pA)')
            data.add_value('Y noise (pA)')
    
data.create_file()
data.copy_file('3D_twosource_sweep.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep

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
        smbgate.set_RF_frequency(RF_start)
        smb.set_RF_frequency(RF_start+LO_frequency/1000)
        qt.msleep(100*timeconstant)
    elif zvarname == 'tc':
        timeconstant = 10**zvar
        HFlockin.set_timeconstant0(timeconstant)
        settlingtime = 10*timeconstant #s used for wait time, should exceed 50 ms?
    elif zvarname == 'Vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)
    elif zvarname == 'RF_phase':
        smb.set_RF_phase(zvar)
    elif zvarname == 'RFgate_phase':
        smbgate.set_RF_phase(zvar)        

    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    
    
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
        elif yvarname == 'tc':
            timeconstant = 10**yvar
            HFlockin.set_timeconstant0(timeconstant)
            settlingtime = 10*timeconstant #s used for wait time, should exceed 50 ms?
        elif yvarname == 'Vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)
        elif yvarname == 'RF_phase':
            smb.set_RF_phase(yvar)
        elif yvarname == 'RFgate_phase':
            smbgate.set_RF_phase(yvar)                    

        #qt.msleep(.2)

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

        #measure dc current    
        if recorddc:
            i=vm.get_readval()/current_gain*-1e3
        else:
            i=0


            
        #measure forward sweep      
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
        counter = 0
        for f in linspace(RF_start,RF_stop,NoRFsteps):
            smbgate.set_RF_frequency(f)
            smb.set_RF_frequency(f+LO_frequency/1000)


            if measurecollapsedtrace:
                fsl.set_center_frequency(LO_frequency/1000)
                qt.msleep(.02)
                fsl.initiate()
                currentsweepnumber=0
                while currentsweepnumber <= NoAverages:
                    qt.msleep(queryingtime)
                    currentsweepnumber =fsl.get_current_sweep_number() 

                trace=fsl.grab_trace() #actual measurement
                power = mean(trace)
            else:
                qt.msleep(settlingtime)
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
                    if x !=0:
                        theta=arctan(y/x)
                    elif (x !=0)& (y<0):
                        theta = -pi/2
                    elif (x !=0)& (y>0):
                        theta = -pi/2

                    if measurenoise:
                        xnoise = vm.get_readval()*sensitivity_map[lockin.get_sensitivity()]*1e12/10
                        ynoise = vm2.get_readval()*sensitivity_map[lockin.get_sensitivity()]*1e12/10
            #save data
            if measurecollapsedtrace:
                data.add_data_point(f,yvar,zvar,power)
            elif measurenoise==False:
                if scalarsubtractbackground & (yvarname != 'vgate'):
                    r_subtracted = r-r_ref[counter]
                    data.add_data_point(f,yvar,zvar,r_subtracted,r_ref[counter],r,theta,x,y,i)
                else:    
                    data.add_data_point(f,yvar,zvar,r,theta,x,y,i)
            elif measurenoise:
                    data.add_data_point(f,yvar,zvar,r,theta,x,y,i,xnoise,ynoise)

            if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                print 'RF frequency: %sMHz' % f
            counter=counter+1

        data.new_block()
        
        #measure reverse sweep
        if forwardandreverse:
            counter = 0
            for f in linspace(RF_stop,RF_start,NoRFsteps):
                smbgate.set_RF_frequency(f)
                smb.set_RF_frequency(f+LO_frequency/1000)

                qt.msleep(settlingtime)

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
                    data.add_data_point(f,yvar,zvar,r_subtracted,r_ref[counter],r,theta,x,y,i)
                else:    
                    data.add_data_point(f,yvar,zvar,r,theta,x,y,i)

                if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                    print 'RF frequency: %sMHz' % f
                counter=counter+1

            data.new_block()

        if displayintermediatetime:
            inttime = time()
            measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((inttime-begintime)/3600),"m":int(((inttime-begintime)%3600)/60),"s":int(((inttime-begintime)%3600)%60)}
            print 'Measurement time: '+ measurementtimestring
    
    spyview_process(data,RF_start,RF_stop,y_start,y_stop,zvar)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)
plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')


#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)
    ramp(vi,'vdd',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Vdd: %sV' % vi.get_vdd()

smb.set_RF_state(False)
smbgate.set_RF_state(False)

vm.set_trigger_continuous(True)
vm2.set_trigger_continuous(True)
    
                    

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring

data.close_file()

qt.mend()
