import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen3D.py')

begintime = time() #for measurement time calculation
recorddc=True #also record dc current?
recorddceachpoint = True
#forwardandreverse=False #sweep forward and reverse?
highfrequency = True #measure with HFlockin (Zurich Instruments) and use HEMT (set Vdd)?
measurecollapsedtrace = True #measure with R&S spectrum analyzer and record maximum?
returntozero = True #sweep voltages back to zero?
scalarsubtractbackground = False #subtract electrical mixing signal
useattenuators = False #use voltage tunable attenuators
amplitudemodulation = False
usefinegate = True
usetwosourcemixing = True #use two signal generators to generate drive and probe? False uses one signal generator for drive and the same signal mixed with ref out of the lockin

drivemode = 'undriven'

# drivemode:
#'direct_source': use signal generator on source, measure at drive frequency,
#'direct_gate': use signal generator on gate, measure at drive frequency,
#'external mixer': use smbgate signal generator and externally mixed with lockin ref out,
#'two-source': use two signal generators
#'AM_gate': amplitudemodulation on gate
#'undriven': no signal generators used

mixed_drivemode = (drivemode=='external_mixer')|(drivemode=='two-source')|(drivemode=='AM_gate')
direct_drivemode = (drivemode=='direct_source')|(drivemode=='direct_gate')

readoutmode = 'spectrum_analyzer'
#readoutmode='HFlockin','LFlockin','spectrum_analyzer'

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if highfrequency:
    if 'HFlockin' not in instlist:
        HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)
    
if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
    ivvi.set_dac_range(3,10000) #uses altered Optodac.py

if False | ('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgatefine',ivvi,'dac2',10*1000,0.0) #0.1x modulation
    vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
    vi.add_variable_scaled('vdd',ivvi,'dac7',1000,0.0)
    if useattenuators:
        vi.add_variable_scaled('vattplus',ivvi,'dac2',1,0.0)
        vi.add_variable_scaled('vattctrl',ivvi,'dac3',1,0.0)

if ('vm' not in instlist) and recorddc:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')

    
temperature = tempcon.get_kelvinA()
#measurement information
med.set_temperature(temperature)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
med.set_current_gain(current_gain)

#15hr
#set frequencies
RF_start_fixed=200 #MHz
RF_stop_fixed=250 #MHz
RF_step=50#MHz
NoRFsteps = int((RF_stop_fixed-RF_start_fixed)/RF_step + 1)
RF_center = (RF_start_fixed+RF_stop_fixed)/2.0


#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2

coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','RF_voltage':'RF voltage (V)','RF_power':'RF power (dBm)', 'RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','Vdd':'Vdd (V)','tc': 'Logarithm of time constant (log (s))','sweepdirection':'Sweep direction','Vattplus':'Attenuator Voltage+ (V)','Vattctrl':'Attenuator Control Voltage (V)','nothing':'Nothing'}
#set y variable
yvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 997
y_stop = 2900997
y_step = 10000
if yvarname == 'nothing':
    y_stop=y_start
    Noysteps=1
else:
    Noysteps = int((y_stop-y_start)/y_step + 1)


#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = -0.1
z_stop = 0.1
z_step = 0.2
if zvarname == 'nothing':
    z_stop=z_start
    Nozsteps=1
else:
    Nozsteps = abs(int((z_stop-z_start)/z_step) + 1)

#set fixed values
vbias_fixed=0.002 #V
ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)

if (yvarname != 'vgatefine') & (zvarname != 'vgatefine'):
    vgatefine_fixed = 0 #V
    ramp(vi,'vgatefine',vgatefine_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage offset: %sV +++' % vgatefine_fixed

if (yvarname != 'vgate') & (zvarname != 'vgate'):
    vgate_fixed = 6.5 #V
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if (yvarname != 'RF_voltage') & (zvarname != 'RF_voltage'):
    RF_voltage= 1 #V (Currently with 10dB in attenuation before source)
    HFlockin.set_power0(RF_voltage)
    print '+++ RF voltage: %sV +++' % RF_voltage
else:
    HFlockin.set_power0(0)    

if (yvarname != 'RF_power') & (zvarname != 'RF_power'):
    RF_power=0 #dBm (Currently with 10dB in attenuation)   
    smb.set_RF_power(RF_power)
    print '+++ RF power: %sdBm +++' % RF_power
else:
    smb.set_RF_power(-70) 

if (yvarname != 'RFgate_power') & (zvarname != 'RFgate_power'):
    RFgate_power=3 #dBm (Currently with 10dB in attenuation)   
    smbgate.set_RF_power(RFgate_power)
    print '+++ RF gate power: %sdBm +++' % RFgate_power
else:
    smb.set_RF_power(-70)    

if (yvarname != 'f_LO') & (zvarname != 'f_LO'):
    LO_frequency= 45997.0 #997.0 #kHz
    HFlockin.set_frequency0(LO_frequency*1000)
    print '+++ LO frequency: %skHz +++' % LO_frequency

if (yvarname != 'tc') & (zvarname != 'tc'):
    logtimeconstant = -3 #minimum: 780ns ~ 10**(-6.1)
    timeconstant_fixed = 10**logtimeconstant
    HFlockin.set_timeconstant0(timeconstant_fixed) #timeconstant_fixed
    settlingtime = 10*timeconstant_fixed #s used for wait time, should exceed 50 ms?
    print '+++ timeconstant: %ss +++' % timeconstant_fixed

if (yvarname != 'Vdd') & (zvarname != 'Vdd'):
    Vdd_fixed = 0.7 # 1 V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

if (yvarname != 'sweepdirection') & (zvarname != 'sweepdirection'):
    RF_start = RF_start_fixed
    RF_stop = RF_stop_fixed
    print '+++ Sweep direction: forward +++'

if useattenuators:
    if (yvarname != 'Vattplus') & (zvarname != 'Vattplus'):
        Vattplus= 0#4999 #mV
        vi.set_vattplus(Vattplus)
        print '+++ Attenuator Voltage+: %sV +++' % Vattplus

    if (yvarname != 'Vattctrl') & (zvarname != 'Vattctrl'):
        Vattctrl= 0#5000 #mV
        vi.set_vattctrl(Vattctrl)
        print '+++ Attenuator Voltage+: %sV +++' % Vattctrl

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

#set gate voltage to measure background signal
if scalarsubtractbackground:
    vgate_ref = 0 #V

#set filename
if highfrequency:
    filename='lg-04xx31b2_2D_HF_twosource_mixed_vs_'+yvarname+'_and_'+zvarname
else:
    filename='lg-04xx31b2_2D_twosource_mixed_vs_'+yvarname+'_and_'+zvarname
    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the high-frequency lockin
if highfrequency:
    HFlockin.set_reference('Internal')
    HFlockin.set_output_switch0(1) #0 = Signal Output 1, 1 = Signal Output 2
    HFlockin.set_input_range0(0.1) #V 0.02
    HFlockin.set_input_range1(0.3) #V
    HFlockin.set_impedance50Ohm0(True)
    HFlockin.set_external_clock(True)

#ready the smb
if drivemode == 'undriven':
    smbgate.set_RF_state(False)
    smb.set_RF_state(False)
elif drivemode == 'two-source':
    smbgate.set_RF_state(True)
    smb.set_RF_state(True)
    smb.set_reference('EXT')
    smb.get_all()
elif drivemode == 'AM_gate':
    smbgate.set_RF_state(True)
    smbgate.set_AM_state(True)
    smbgate.set_Modulation_state(True)
    smbgate.set_AM_source('EXT')
    smbgate.set_AM_depth(100)
elif drivemode == 'direct_source':
    smbgate.set_RF_state(True)
    smb.set_RF_state(True)
else:
    smbgate.set_RF_state(True)
    
smbgate.set_reference('INT')
smbgate.get_all()

if recorddc:
#ready vm
    vm.get_all()
    vm.set_trigger_continuous(False)
    ramp(vi,'vbias',0.001,sweepstep,sweeptime)

#ready the fsl
if readoutmode == 'spectrum_analyzer':
    fsl.set_trace_continuous(True)
    fsl.set_filter_type('FFT') #use 'NORM' above 30 kHz
    fsl.set_trace_mode('AVER')
    fsl.set_number_of_sweeps(30000)
    bandwidth = 0.0011 # MHz
    fsl.set_resolution_bandwidth(bandwidth) #MHz

    sweeppoints=101
    fsl.set_sweeppoints(sweeppoints)

    fstep=span/(sweeppoints-1.0)
    queryingtime = 0.1 # don't use lower because has not "settled"
    NoAverages = 2
    
    if drivemode=='undriven':
        span = RF_stop-RF_start
    else:
        span = 0.2*bandwidth # MHz
        

    fsl.set_span(span)

if drivemode == 'undriven':
    RF_array_fixed=linspace(RF_start_fixed,RF_stop_fixed,sweeppoints)
else:
    RF_array_fixed=linspace(RF_start_fixed,RF_stop_fixed,NoRFsteps)

#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])

if readoutmode=='spectrum_analyzer':
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
    
data.create_file()
data.copy_file('3D_twosource_mixed_sweep.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep

for zvar in linspace(z_start,z_stop,Nozsteps):


    #set z variable
    if zvarname == 'vgatefine':
        ramp(vi,'vgatefine',zvar,sweepstep,sweeptime)
    elif zvarname == 'vgate':
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'RF_power':
        smb.set_RF_power(zvar)
    elif zvarname == 'RF_power':
        smb.set_RF_power(zvar)        
    elif zvarname == 'RFgate_power':
        smbgate.set_RF_power(zvar)
    elif zvarname == 'f_LO':
        LO_frequency=zvar
        if usetwosourcemixing:
            smbgate.set_RF_frequency(RF_start)
            smb.set_RF_frequency(RF_start+LO_frequency/1000)
        else:
            HFlockin.set_frequency0(LO_frequency*1000)
    elif zvarname == 'tc':
        vartimeconstant=10**zvar
        HFlockin.set_timeconstant0(vartimeconstant)
        settlingtime = 10*vartimeconstant#s used for wait time, should exceed 50 ms?
    elif zvarname == 'Vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)
    elif zvarname == 'sweepdirection':
        if zvar == 1:
            RF_start = RF_start_fixed
            RF_stop = RF_stop_fixed
        elif zvar == -1:
            RF_start = RF_stop_fixed
            RF_stop = RF_start_fixed
    elif zvarname == 'Vattplus':
        vi.set_vattplus(zvar)
    elif zvarname == 'Vattctrl':
        vi.set_vattctrl(zvar)

    if drivemode == 'undriven':
        z_array=zvar*ones(sweeppoints)
    else:
        z_array=zvar*ones(NoRFsteps)
    
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    
    
    for yvar in linspace(y_start,y_stop,Noysteps):
        #set y variable
        if yvarname == 'vgatefine':
            ramp(vi,'vgatefine',yvar,sweepstep,sweeptime)
        elif yvarname == 'vgate':
            ramp(vi,'vgate',yvar,sweepstep,sweeptime)
        elif yvarname == 'RF_power':
            smb.set_RF_power(yvar)
        elif yvarname == 'RFgate_power':
            smbgate.set_RF_power(yvar)
        elif yvarname == 'f_LO':
            LO_frequency=yvar
            if usetwosourcemixing:
                smbgate.set_RF_frequency(RF_start)
                smb.set_RF_frequency(RF_start+LO_frequency/1000)
            else:
                HFlockin.set_frequency0(LO_frequency*1000)
        elif yvarname == 'tc':
            vartimeconstant = 10**yvar
            HFlockin.set_timeconstant0(vartimeconstant)
            settlingtime = 10*vartimeconstant #s used for wait time, should exceed 50 ms?
        elif yvarname == 'Vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)        
        elif yvarname == 'sweepdirection':
            if yvar == 1:
                RF_start = RF_start_fixed
                RF_stop = RF_stop_fixed
            elif yvar == -1:
                RF_start = RF_stop_fixed
                RF_stop = RF_start_fixed          
        elif yvarname == 'Vattplus':
            vi.set_vattplus(yvar)
        elif yvarname == 'Vattctrl':
            vi.set_vattctrl(yvar)
            
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar

        if drivemode == 'undriven':
            y_array=zvar*ones(sweeppoints)
        else:
            y_array=zvar*ones(NoRFsteps)
            
        qt.msleep(.2)

        #scalar subtraction of background (unavailable if gate voltage is looped)
        if scalarsubtractbackground & ((yvarname != 'vgate')|(yvarname != 'vgatefine')):
            vg_array = [vgate_fixed,vgate_ref]
            x_ref=zeros(NoRFsteps)
            y_ref=zeros(NoRFsteps)
            r_ref=zeros(NoRFsteps)
        else:
            vg_array = [vgate_fixed]

        x=zeros(NoRFsteps)
        y=zeros(NoRFsteps)
        r=zeros(NoRFsteps)
        theta=zeros(NoRFsteps)
        power=zeros(NoRFsteps)

        #measure dc current    
        if recorddc:
            i=vm.get_readval()/current_gain*-1e3
        else:
            i=0
        i_array = i*ones(NoRFsteps)
        
        for vg in vg_array:

            ramp(vi,'vgate',vg,sweepstep,sweeptime)
            print '^^^Gate voltage: %s ^^^' % vg
            


            
            counter = 0

            if drivemode == 'undriven':
                if readoutmode == 'spectrum_analyzer':
                    fsl.set_center_frequency(RF_center)
                    qt.msleep(.02)
                    fsl.initiate()
                    currentsweepnumber=0
                    while currentsweepnumber <= NoAverages:
                        qt.msleep(queryingtime)
                        currentsweepnumber =fsl.get_current_sweep_number() 

                    trace=fsl.grab_trace() #actual measurement
                    power = trace
            else:
                for f in linspace(RF_start,RF_stop,NoRFsteps):
                    smbgate.set_RF_frequency(f)

                    if drivemode == 'two-source':
                        smb.set_RF_frequency(f+LO_frequency/1000)
                    
                    if (readoutmode == 'spectrum_analyzer'):
                        if mixed_readoutmode:
                            fsl.set_center_frequency(LO_frequency/1000)
                        if direct_readoutmode:
                            fsl.set_center_frequency(RF_center)
                            
                        qt.msleep(.02)
                        fsl.initiate()
                        currentsweepnumber=0
                        while currentsweepnumber <= NoAverages:
                            qt.msleep(queryingtime)
                            currentsweepnumber =fsl.get_current_sweep_number() 

                        trace=fsl.grab_trace() #actual measurement
                        power[counter] = mean(trace)
                    elif readoutmode == 'HFlockin':
                        qt.msleep(settlingtime)
                        if vg == vgate_ref:
                            x_ref[counter]=HFlockin.get_x()
                            y_ref[counter]=HFlockin.get_y()
                            r_ref[counter]=HFlockin.get_amplitude()
                        else:
                            x[counter]=HFlockin.get_x()
                            y[counter]=HFlockin.get_y()
                            r[counter]=HFlockin.get_amplitude()
                            theta[counter] = HFlockin.get_phase()
                    elif readoutmode == 'LFlockin':
                        qt.msleep(settlingtime)
                        rawdat=lockin.query('SNAP?1,2')
                        datlist=rawdat.split(',')
                        x[counter]=1e12*float(datlist[0])
                        y[counter]=1e12*float(datlist[1])
                        r[counter]=sqrt(x[counter]**2+y[counter]**2)
                        theta[counter]=arctan(y[counter]/x[counter])
                            
                if scalarsubtractbackground & (yvarname != 'vgate'):
                    r_subtracted = r-r_ref

                if recorddceachpoint:
                    i_array[counter] = vm.get_readval()/current_gain*-1e3
            
                if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                    print 'RF frequency: %sMHz' % f
                    counter=counter+1

        #save data
        if ((yvarname == 'sweepdirection') & (yvar==-1)) | ((zvarname == 'sweepdirection') & (zvar==-1)):
            r = np.flipud(r)
            theta = np.flipud(theta)
            x = np.flipud(x)
            y = np.flipud(y)
            if scalarsubtractbackground & (yvarname != 'vgate'):
                r_subtracted = np.flipud(r_subtracted)
                r_ref= np.flipud(r_ref)

        if readoutmode == 'spectrum_analyzer':
            print 'hier'
            data.add_data_point(RF_array_fixed,y_array,z_array,power)
        else:
            if scalarsubtractbackground & (yvarname != 'vgate'):
                data.add_data_point(RF_array_fixed,y_array,z_array,r_subtracted,r_ref,r,theta,x,y,i_array)
            else:    
                data.add_data_point(RF_array_fixed,y_array,z_array,r,theta,x,y,i_array)

        data.new_block()
        if displayintermediatetime:
            inttime = time()
            measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((inttime-begintime)/3600),"m":int(((inttime-begintime)%3600)/60),"s":int(((inttime-begintime)%3600)%60)}
            print 'Measurement time: '+ measurementtimestring

    spyview_process(data,RF_stop,RF_start,y_start,y_stop,zvar)    
    

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)
plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')


#reset voltages
if returntozero:
    ramp(vi,'vgatefine',0,sweepstep,sweeptime)
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)
    if highfrequency:
        ramp(vi,'vdd',0,sweepstep,sweeptime)
    if useattenuators:
        vi.set_vattplus(0)
        vi.set_vattctrl(0)        

print 'Gate voltage offset: %sV' % vi.get_vgatefine()
print 'Gate voltage: %sV' % vi.get_vgate()
print 'Bias voltage: %sV' % vi.get_vbias()
print 'Vdd: %sV' % vi.get_vdd()
if useattenuators:
    print 'Attenuator voltage+: %sV' % vi.get_vattplus()
    print 'Attenuator control voltage: %sV' % vi.get_vattctrl()

smbgate.set_RF_state(False)
if recorddc:
    vm.set_trigger_continuous(True)

if 'drivemode'=='AM_gate':
    smbgate.set_AM_state(False)
    smbgate.set_Modulation_state(False)
          

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring

data.close_file()

qt.mend()
