import qt
import sys
from time import time
import numpy
execfile('ramp.py')
execfile('metagen3D.py')
#execfile('component1.py')
def average(s): return sum(s) * 1.0/ len(s)
def stddev(s): return sqrt(average(map(lambda x: (x-average(s))**2,s)))


begintime = time() #for measurement time calculation
inttime = time()
recorddc=True #also record dc current?
recorddceachpoint = True
#forwardandreverse=False #sweep forward and reverse?
highfrequency = True #measure with HFlockin (Zurich Instruments) and use HEMT (set Vdd)?
measurecollapsedtrace = False #measure with R&S spectrum analyzer and record maximum?
returntozero = True #sweep voltages back to zero?
scalarsubtractbackground = False #subtract electrical mixing signal
useattenuators = False #use voltage tunable attenuators
amplitudemodulation = False
usefinegate = False
usetwosourcemixing = False #use two signal generators to generate drive and probe? False uses one signal generator for drive and the same signal mixed with ref out of the lockin
displayintermediatetime=True
recordxyoscil=True

IVVIactivate = False

drivemode = 'external_mixer'

# drivemode:
#'direct_source': use signal generator on source, measure at drive frequency,
#'direct_gate': use signal generator on gate, measure at drive frequency,
#'external_mixer': use smbgate signal generator and externally mixed with lockin ref out,
#'two-source': use two signal generators
#'two-source_noise': use smb on source to probe, measure noise at difference frequency
#'AM_gate': amplitudemodulation on gate
#'undriven': no signal generators used

mixed_drivemode = (drivemode=='external_mixer')|(drivemode=='two-source')|(drivemode=='AM_gate')
direct_drivemode = (drivemode=='direct_source')|(drivemode=='direct_gate')

readoutmode = 'HFlockin'
#readoutmode='HFlockin','LFlockin','spectrum_analyzer','none' (dc only),'oscilloscope','HFoscil'

externality = 'nothing'
#'RFswitch','attenuator' (not programmed yet) 

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


if readoutmode == 'oscilloscope':
    oscil = qt.instruments.create('oscil','Rigol_DS1102E',address='USB0::0x1AB1::0x0588::DS1EB122904339::INSTR')
if False | ('HFoscil' not in instlist):
    if readoutmode == 'HFoscil':
        HFoscil = qt.instruments.create('HFoscil','RS_RTO_1014',address='TCPIP0::192.168.100.101::inst0::INSTR')

if highfrequency:
    if 'HFlockin' not in instlist:
        HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)

#if 'fsl' not in instlist:
#    fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')
    
if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')


if IVVIactivate:
    if 'ivvi' not in instlist:
        ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
        ivvi.set_dac_range(3,10000) #uses altered Optodac.py


if False | ('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')

    if IVVIactivate:
            # was used for IVVI
            vi.add_variable_scaled('vgatefine',ivvi,'dac2',10*1000,0.0) #0.1x modulation
            vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
            vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
            vi.add_variable_scaled('vdd',ivvi,'dac7',1000,0.0)
            if useattenuators:
                vi.add_variable_scaled('vattplus',ivvi,'dac2',1,0.0)
                vi.add_variable_scaled('vattctrl',ivvi,'dac3',1,0.0)

            if externality == 'RFswitch':
                vi.add_variable_scaled('vRFplus',lockin,'out1',1,0.0)
                vi.add_variable_scaled('vRFminus',lockin,'out2',1,0.0)

    else:
            vi.add_variable_scaled('vgate',lockin,'out1',1,0.0) #because ivvi.set_dac is in mV
            vi.add_variable_scaled('vgatefine',lockin,'out2',10,0.0) #0.1x modulation
            vi.add_variable_scaled('vbias',lockin,'out3',10,0.0)
            vi.add_variable_scaled('vdd',lockin,'out4',1,0.0)
            if useattenuators:
                vi.add_variable_scaled('vattplus',lockin,'out2',1,0.0)
                vi.add_variable_scaled('vattctrl',lockin,'out1',1,0.0)

            if externality == 'RFswitch':
                HFlockin.set_auxmode(2,-1)  #sets aux 3 to manual
                HFlockin.set_auxmode(3,-1)  #sets aux 4 to manual
                vi.add_variable_scaled('vRFplus',HFlockin,'auxoffset2',1,0.0)
                vi.add_variable_scaled('vRFminus',HFlockin,'auxoffset3',1,0.0)
                
                

    
if False | (('vm' not in instlist) and recorddc):
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

if False | ('smb' not in instlist):
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')

if 'tempcon' not in instlist:
    tempcon = qt.instruments.create('tempcon','Lakeshore_331',address='GPIB::12')


temperature = 300#tempcon.get_kelvinA()
#measurement information
med.set_temperature(temperature)
device = 'lg-04UR21c6'
med.set_device(device)
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.001 #GV/A=mV/pA
med.set_current_gain(current_gain)

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

if drivemode == 'two-source_noise':
    Nonoise = 4000 #Number of x and y to determine standard deviation
    NEPBWfactor = (0.250, 0.125, 0.094, 0.078, 0.068, 0.062, 0.056, 0.052) # fNEPBW=NEPBW/tc, for filterorder 1 to 8 (ZIlockin manual)
    
#set frequencies
RF_start_fixed=120 #MHz
RF_stop_fixed=160 #MHz
RF_step=0.1#0.4 #MHz
NoRFsteps = int((RF_stop_fixed-RF_start_fixed)/RF_step + 1)
RF_center = (RF_start_fixed+RF_stop_fixed)/2.0
RF_array_fixed = linspace(RF_start_fixed,RF_stop_fixed,NoRFsteps)

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2

coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','vbias':'Bias voltage (V)','RF_voltage':'RF voltage (V)','RF_power':'RF power (dBm)', 'RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','Vdd':'Vdd (V)','tc': 'Logarithm of time constant (log (s))','sweepdirection':'Sweep direction','Vattplus':'Attenuator Voltage+ (V)','Vattctrl':'Attenuator Control Voltage (V)','nothing':'Nothing'}
#set y variable
yvarname = 'vgate' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 2
y_stop = 4
y_step = 0.02
if yvarname == 'nothing':
    y_stop=y_start
    Noysteps=1
else:
    Noysteps = round((y_stop-y_start)/y_step + 1)


#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = 0#0.4#log10(780e-9)
z_stop = 0#0.5#-5
z_step = 1#0.1#-5-log10(780e-9)
if zvarname == 'nothing':
    z_start=1
    Nozsteps=1
    z_stop = Nozsteps
else:
    Nozsteps = abs(round((z_stop-z_start)/z_step) + 1)

#set fixed values



if (yvarname != 'vgatefine') & (zvarname != 'vgatefine'):
    vgatefine_fixed = 0 #V
    ramp(vi,'vgatefine',vgatefine_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage offset: %sV +++' % vgatefine_fixed

if (yvarname != 'vgate') & (zvarname != 'vgate'):
    vgate_fixed = 0 #V
    vgate=vgate_fixed
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if (yvarname != 'vbias') & (zvarname != 'vbias'):
    vbias_fixed=0.005 #V
    ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
    print '+++ Bias voltage: %sV +++' % vbias_fixed    

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
    RFgate_power=0 #dBm (Currently with 10dB in attenuation)   
    smbgate.set_RF_power(RFgate_power)
    print '+++ RF gate power: %sdBm +++' % RFgate_power
else:
    smb.set_RF_power(-70)    

if (yvarname != 'f_LO') & (zvarname != 'f_LO'):
    LO_frequency= 5997.0 #997.0 #kHz
    HFlockin.set_frequency0(LO_frequency*1000)
    print '+++ LO frequency: %skHz +++' % LO_frequency

if (yvarname != 'tc') & (zvarname != 'tc'):
    logtimeconstant = -4 # log10(780e-9) #minimum: 780ns ~ 10**(-6.1)
    timeconstant = 10**logtimeconstant
    HFlockin.set_timeconstant0(timeconstant) #timeconstant_fixed
    settlingtime = 10*timeconstant #s used for wait time, should exceed 50 ms?
    if readoutmode == 'oscilloscope':
        oscil.set_time_scale(timeconstant)
    elif readoutmode == 'HFoscil':
        HFoscil.set_time_scale(10*timeconstant)        
    print '+++ timeconstant: %ss +++' % timeconstant

if (yvarname != 'Vdd') & (zvarname != 'Vdd'):
    Vdd_fixed = 1 # 1 V @ RT, 0.5 V @ 77K
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

if externality == 'RFswitch':
    vi.set_vRFplus(5)
    vi.set_vRFminus(-5)
    smb.set_pulse_state(False)
    smb.set_pulse_period(1000) #us
    smb.set_pulse_width(500) #us

#set gate voltage to measure background signal
vgate_ref = 0 #V

#set filename
if highfrequency:
    filename=device+'_'+drivemode+'_'+readoutmode+'_vs_'+yvarname+'_and_'+zvarname
    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the high-frequency lockin
if (readoutmode == 'HFlockin') | (readoutmode == 'oscilloscope') | (readoutmode == 'HFoscil'):
    HFlockin.set_reference('Internal')
    HFlockin.set_output_switch0(1) #0 = Signal Output 1, 1 = Signal Output 2
    HFlockin.set_input_range0(1) #V 0.02
    HFlockin.set_input_range1(0.3) #V
    HFlockin.set_impedance50Ohm0(True)
    HFlockin.set_external_clock(True)
    filterorder = 1
    HFlockin.set_filter_order0(filterorder)

#ready the oscilloscope
if readoutmode == 'oscilloscope':
    oscil.set_waveform_mode('RAW') #'RAW' or 'NORMAL'
    oscil.set_memory_depth('NORMAL') #'LONG' or 'NORMAL'
    Notimesteps = 8192 #'RAW'+'NORMAL' 8192, 'NORMAL'+'NORMAL' 600
    #oscil.set_time_scale(5e-9)
if readoutmode == 'HFoscil':
    Notraces = 10 #how many traces to average
    Notimesteps = 1000 #how many points in trace
    HFoscil.set_record_length(Notimesteps)
    HFoscil.set_voltage_scale1(0.4)
    HFoscil.set_voltage_position1(0)
    if recordxyoscil:
        HFoscil.set_voltage_scale3(0.20)
        HFoscil.set_voltage_position3(-1)
        HFoscil.set_voltage_scale4(0.40)
        HFoscil.set_voltage_position4(3.5)

    HFoscil.set_voltage_scale2(0.5)
    HFoscil.set_voltage_position2(-3.8)
    #HFoscil.set_time_position(-7e-6)


#ready the smb
if drivemode == 'undriven':
    smbgate.set_RF_state(False)
    smb.set_RF_state(False)
elif drivemode == 'two-source':
    smbgate.set_RF_state(True)
    smb.set_RF_state(True)
    smb.set_reference('EXT')
    smb.get_all()
elif drivemode == 'two-source_noise':
    smbgate.set_RF_state(False)
    smb.set_RF_state(True)
    smb.get_all()
    HFlockin.set_output_switch0(0) 
elif drivemode == 'AM_gate':
    smbgate.set_RF_state(True)
    smbgate.set_AM_state(True)
    smbgate.set_Modulation_state(True)
    smbgate.set_AM_source('EXT')
    smbgate.set_AM_depth(100)
elif drivemode == 'direct_source':
    smb.set_RF_state(True)
else:
    smbgate.set_RF_state(True)
    
smbgate.set_reference('INT')
smbgate.get_all()

if recorddc:
#ready vm
    vm.get_all()
    vm.set_trigger_continuous(False)
    
#ready the fsl
if readoutmode == 'spectrum_analyzer':
    fsl.set_trace_continuous(True)
    fsl.set_filter_type('FFT') #use 'NORM' above 30 kHz
    fsl.set_trace_mode('AVER')
    fsl.set_number_of_sweeps(30000)
    bandwidth = 0.0011 # MHz
    fsl.set_resolution_bandwidth(bandwidth) #MHz

    
    

    
    queryingtime = 0.1 # don't use lower because has not "settled"
    NoAverages = 10
    
    if drivemode=='undriven':
        span = RF_stop-RF_start
        fsl.set_sweeppoints(NoRFsteps)
    else:
        span = 0.2*bandwidth # MHz
        fsl.set_sweeppoints(101)

    fsl.set_span(span)    
    fstep=span/(NoRFsteps-1.0)
    


#Set up datafile
data = qt.Data(name=filename)
if (readoutmode == 'oscilloscope')|(readoutmode == 'HFoscil'):
    data.add_coordinate('Time (s)')
    
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])

if (readoutmode != 'oscilloscope')&(readoutmode != 'HFoscil'):
    data.add_coordinate(coordinate_names[zvarname])

if readoutmode=='spectrum_analyzer':
    data.add_value('Power (dBm)')
    data.add_value('DC (pA)')
elif readoutmode=='none':
    data.add_value('DC (pA)')
else:
    if scalarsubtractbackground & (yvarname != 'vgate'):
        data.add_value('R_subtracted (V)')
        data.add_value('R_ref (V)')
                        
    if readoutmode == 'HFlockin':
        if drivemode == 'two-source_noise':
            data.add_value('R (Vrms/sqrt(Hz))')
            data.add_value('theta ((radrms/sqrt(Hz))')
            data.add_value('X (Vrms/sqrt(Hz))')
            data.add_value('Y (Vrms/sqrt(Hz))')
            data.add_value('DC (pA)')
        else:
            data.add_value('R (V)')
            data.add_value('theta (rad)')
            data.add_value('X (V)')
            data.add_value('Y (V)')
            data.add_value('DC (pA)')
    elif readoutmode == 'LFlockin':
        data.add_value('R (pA)')
        data.add_value('theta (rad)')
        data.add_value('X (pA)')
        data.add_value('Y (pA)')
        data.add_value('DC (pA)')
    elif (readoutmode == 'oscilloscope') | (readoutmode == 'HFoscil'):
        data.add_value('Channel 1 voltage (V)') #R
        data.add_value('Channel 2 voltage (V)') #pulse
        if recordxyoscil:
            data.add_value('Channel 3 voltage (V)') #X
            data.add_value('Channel 4 voltage (V)') #Y
            
        data.add_value('DC (pA)')
        
data.create_file()
data.copy_file('ND_frequency_trace.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep

for zvar in linspace(z_start,z_stop,Nozsteps):


    #set z variable
    if zvarname == 'vgatefine':
        ramp(vi,'vgatefine',zvar,sweepstep,sweeptime)
    elif zvarname == 'vgate':
        vgate = zvar
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'vbias':
        ramp(vi,'vbias',zvar,sweepstep,sweeptime)        
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
        timeconstant=10**zvar
        HFlockin.set_timeconstant0(timeconstant)
        settlingtime = 10*timeconstant#s used for wait time, should exceed 50 ms?
        if readoutmode == 'oscilloscope':
            oscil.set_time_scale(timeconstant)
        elif readoutmode == 'HFoscil':
            HFoscil.set_time_scale(20e-6)
            #HFoscil.set_time_scale(timeconstant)
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

    if (readoutmode == 'oscilloscope')|(readoutmode == 'HFoscil'):
        z_array=zvar*ones(Notimesteps)
    else:
        z_array=zvar*ones(NoRFsteps)
    
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    
    
    for yvar in linspace(y_start,y_stop,Noysteps):
        #set y variable
        if yvarname == 'vgatefine':
            ramp(vi,'vgatefine',yvar,sweepstep,sweeptime)
        elif yvarname == 'vgate':
            vgate = yvar
            ramp(vi,'vgate',yvar,sweepstep,sweeptime)
        elif yvarname == 'vbias':
            ramp(vi,'vbias',yvar,sweepstep,sweeptime)                    
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
            timeconstant = 10**yvar
            HFlockin.set_timeconstant0(timeconstant)
            settlingtime = 10*timeconstant #s used for wait time, should exceed 50 ms?
            if readoutmode == 'oscilloscope':
                oscil.set_time_scale(timeconstant)
            elif readoutmode == 'HFoscil':
                HFoscil.set_time_scale(timeconstant)
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

        if (readoutmode == 'oscilloscope') | (readoutmode == 'HFoscil'):
            y_array=yvar*ones(Notimesteps)
        else:
            y_array=yvar*ones(NoRFsteps)
        
            
        

        #scalar subtraction of background (unavailable if gate voltage is looped)
        if scalarsubtractbackground & ((yvarname != 'vgate')|(yvarname != 'vgatefine')):
            vg_array = [vgate_fixed,vgate_ref]
            x_ref=zeros(NoRFsteps)
            y_ref=zeros(NoRFsteps)
            r_ref=zeros(NoRFsteps)
        else:
            vg_array = [vgate]

        if drivemode == 'two-source_noise':
            x_interm=zeros(Nonoise)
            y_interm=zeros(Nonoise)
            r_interm=zeros(Nonoise)
            theta_interm=zeros(Nonoise)
        
        x=zeros(NoRFsteps)
        y=zeros(NoRFsteps)
        r=zeros(NoRFsteps)
        theta=zeros(NoRFsteps)
        power=zeros(NoRFsteps)

        qt.msleep(.1)
        #measure dc current    
        if recorddc:
            i=vm.get_readval()/current_gain*-1e3
        else:
            i=0
        if (readoutmode == 'oscilloscope') | (readoutmode == 'HFoscil'):
            i_array = i*ones(Notimesteps)
        else:
            i_array = i*ones(NoRFsteps)
        
        for vg in vg_array:

            #ramp(vi,'vgate',vg,sweepstep,sweeptime)
            #print '^^^Gate voltage: %s ^^^' % vg
            
            

            
            

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
                counter = 0
                for f in linspace(RF_start,RF_stop,NoRFsteps):
                    if drivemode == 'direct_source':
                        smb.set_RF_frequency(f)
                    elif drivemode == 'two-source':
                        smbgate.set_RF_frequency(f)
                        smb.set_RF_frequency(f+LO_frequency/1000)
                    elif drivemode == 'two-source_noise':
                        smb.set_RF_frequency(f+LO_frequency/1000)
                    else:
                        smbgate.set_RF_frequency(f)

                    if (readoutmode == 'spectrum_analyzer'):
                        if mixed_drivemode:
                            fsl.set_center_frequency(LO_frequency/1000)
                        if direct_drivemode:
                            fsl.set_center_frequency(f)
                            
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
                        if drivemode == 'two-source_noise':
                            for noisecounter in range(0,Nonoise):
                                sample = HFlockin.get_sample()
                                x_interm[noisecounter]=float(sample['x'])
                                y_interm[noisecounter]=float(sample['y'])
                                r_interm[noisecounter]=numpy.sqrt(float(sample['x'])**2+float(sample['y'])**2)
                                theta_interm[noisecounter] = numpy.arctan(float(sample['y'])/float(sample['x']))
                            
                            x[counter] = stddev(x_interm)/sqrt(NEPBWfactor[filterorder]/timeconstant)
                            y[counter] = stddev(y_interm)/sqrt(NEPBWfactor[filterorder]/timeconstant)
                            r[counter] = stddev(r_interm)/sqrt(NEPBWfactor[filterorder]/timeconstant)
                            theta[counter] = stddev(theta_interm)/sqrt(NEPBWfactor[filterorder]/timeconstant)
                        else:
                            if (vg == vgate_ref) & (len(vg_array)==2):
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
                    elif readoutmode == 'oscilloscope':
                        RF_array_fixed=f*ones(Notimesteps)
                        qt.msleep(settlingtime)
                        oscil.stop()
                        time_array, amplitude_array = oscil.get_trace('CHAN1')
                        time2_array, amplitude2_array = oscil.get_trace('CHAN2')
                        oscil.run()
                        data.add_data_point(time_array, RF_array_fixed,y_array,amplitude_array,amplitude2_array,i_array)
                        data.new_block()
                    elif readoutmode == 'HFoscil':
                        RF_array_fixed=f*ones(Notimesteps)
                        qt.msleep(0.2)#settlingtime)
                        
                        time_array, amplitude_array = HFoscil.get_trace(1)
                        time2_array, amplitude2_array = HFoscil.get_trace(2)

                        if recordxyoscil:
                            time3_array, amplitude3_array = HFoscil.get_trace(3)
                            time4_array, amplitude4_array = HFoscil.get_trace(4)

                        if recordxyoscil:
                            data.add_data_point(time_array, RF_array_fixed,y_array,amplitude_array,amplitude2_array,amplitude3_array,amplitude4_array,i_array)
                        else:
                            data.add_data_point(time_array, RF_array_fixed,y_array,amplitude_array,amplitude2_array,i_array)
                        data.new_block()
                        #print amplitude_array[1]
                        #HFoscil.stop()
                        #HFoscil.run()
                    
                    if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                        print 'RF frequency: %sMHz' % f
                        
                    if scalarsubtractbackground & (yvarname != 'vgate'):
                        r_subtracted = r-r_ref

                    if recorddceachpoint:
                        if readoutmode == 'oscilloscope':
                            i_array=vm.get_readval()/current_gain*-1e3*ones(len(time_array))
                        else:
                            i_array[counter] = vm.get_readval()/current_gain*-1e3
                    counter=counter+1

        if (readoutmode == 'oscilloscope')|(readoutmode == 'HFoscil'):
            spyview_process(data,min(time_array),max(time_array),RF_start,RF_stop,yvar)
                

        #save data
        if (readoutmode != 'oscilloscope') & (readoutmode != 'HFoscil'):
            if ((yvarname == 'sweepdirection') & (yvar==-1)) | ((zvarname == 'sweepdirection') & (zvar==-1)):
                r = numpy.flipud(r)
                theta = numpy.flipud(theta)
                x = numpy.flipud(x)
                y = numpy.flipud(y)
                if scalarsubtractbackground & (yvarname != 'vgate'):
                    r_subtracted = numpy.flipud(r_subtracted)
                    r_ref= numpy.flipud(r_ref)

            if readoutmode == 'spectrum_analyzer':
                data.add_data_point(RF_array_fixed,y_array,z_array,power,i_array)
            elif readoutmode == 'none':
                data.add_data_point(RF_array_fixed,y_array,z_array,i_array)
            else:
                if scalarsubtractbackground & (yvarname != 'vgate'):
                    data.add_data_point(RF_array_fixed,y_array,z_array,r_subtracted,r_ref,r,theta,x,y,i_array)
                else:    
                    data.add_data_point(RF_array_fixed,y_array,z_array,r,theta,x,y,i_array)
      
            data.new_block()
            
        if displayintermediatetime:
            deltatime = time()-inttime
            totaltime = deltatime*Noysteps*Nozsteps
            inttime = time()
            intmeasurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((inttime-begintime)/3600),"m":int(((inttime-begintime)%3600)/60),"s":int(((inttime-begintime)%3600)%60)}
            totalmeasurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((totaltime)/3600),"m":int(((totaltime)%3600)/60),"s":int(((totaltime)%3600)%60)}
            print 'Current measurement time: '+ intmeasurementtimestring
            print 'Estimated total measurement time: '+ totalmeasurementtimestring

    if (readoutmode != 'oscilloscope') & (readoutmode != 'HFoscil'):
        spyview_process(data,RF_start,RF_stop,y_start,y_stop,zvar)    
    

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
plot2dx.add_data(data, coorddim=0, valdim=4)
plot2dx.update
if (readoutmode != 'oscilloscope') & (readoutmode != 'HFoscil'):    
    plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)
    plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
    plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')
    #plot2dc = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=7)
    #plot2dc.save_png(filepath=data.get_dir()+'\\'+'plot2dc.png')

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
    if externality == 'RFswitch':
        vi.set_vRFplus(0)
        vi.set_vRFminus(0)

print 'Gate voltage offset: %sV' % vi.get_vgatefine()
print 'Gate voltage: %sV' % vi.get_vgate()
print 'Bias voltage: %sV' % vi.get_vbias()
print 'Vdd: %sV' % vi.get_vdd()
if useattenuators:
    print 'Attenuator voltage+: %sV' % vi.get_vattplus()
    print 'Attenuator control voltage: %sV' % vi.get_vattctrl()
if externality == 'RFswitch':
    print 'RFswitch voltage+: %sV' % vi.get_vRFplus()
    print 'RFswitch voltage-: %sV' % vi.get_vRFminus()

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
