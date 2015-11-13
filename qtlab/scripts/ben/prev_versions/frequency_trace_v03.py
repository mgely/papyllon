import qt
import sys
from time import time
import numpy
#execfile('ramp.py') included in frequency_trace_routines.py
#execfile('metagen3D_ben.py') included in frequency_trace_routines.py
execfile('frequency_trace_routines_v02.py')
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
recordxyoscil=False
IVVIactivate = False #set this to False if no IVVI rack is available then it will use the lockins to send the voltages.
drivemode = 'external_mixer'
'''
drivemode:
'direct_source': use signal generator on source, measure at drive frequency,
'direct_gate': use signal generator on gate, measure at drive frequency,
'external_mixer': use smbgate signal generator and externally mixed with lockin ref out,
'two-source': use two signal generators
'two-source_noise': use smb on source to probe, measure noise at difference frequency
'AM_gate': amplitudemodulation on gate
'undriven': no signal generators used
'''
mixed_drivemode = (drivemode=='external_mixer')|(drivemode=='two-source')|(drivemode=='AM_gate')
direct_drivemode = (drivemode=='direct_source')|(drivemode=='direct_gate')
readoutmode = 'HFlockin'
#readoutmode='HFlockin','LFlockin','spectrum_analyzer','none' (dc only),'oscilloscope','HFoscil'
externality = 'nothing'
#'RFswitch','attenuator' (not programmed yet), 'nothing' 

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#install drivers with given settings (prototype of frequency_trace_routines.py )
install_drivers(instlist,
                readoutmode,
                highfrequency,
                externality,
                IVVIactivate)

temperature = 3#tempcon.get_kelvinA()
#measurement information
med.set_temperature(temperature)
device = 'lg-04UR21c6'
med.set_device(device)
med.set_setup('1K dipstick')
med.set_user('Ben')
current_gain = 1e6 # V/A output to Amps
med.set_current_gain(current_gain)

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

if drivemode == 'two-source_noise':
    Nonoise = 4000 #Number of x and y to determine standard deviation
    NEPBWfactor = (0.250, 0.125, 0.094, 0.078, 0.068, 0.062, 0.056, 0.052) # fNEPBW=NEPBW/tc, for filterorder 1 to 8 (ZIlockin manual)
    
#set frequencies
RF_start_fixed=139-30 #MHz #res 1 at 136Mhz 2 at 306MHz
RF_stop_fixed=309+30 #MHz
RF_step=0.1#0.4 #MHz
NoRFsteps = int((RF_stop_fixed-RF_start_fixed)/RF_step + 1)
RF_center = (RF_start_fixed+RF_stop_fixed)/2.0
RF_array_fixed = linspace(RF_start_fixed,RF_stop_fixed,NoRFsteps)

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2

coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','vbias':'Bias voltage (V)','RF_voltage':'RF voltage (V)','RF_power':'RF power (dBm)', 'RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','vdd':'Vdd (V)','tc': 'Logarithm of time constant (log (s))','sweepdirection':'Sweep direction','Vattplus':'Attenuator Voltage+ (V)','Vattctrl':'Attenuator Control Voltage (V)','nothing':'Nothing'}

#set y variable
yvarname = 'vgate' # 'vgate' or 'RF_power' or 'f_LO' or 'vdd' or 'tc'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 0
y_stop = 2
y_step = 0.015
if yvarname == 'nothing':
    y_start=0
    Noysteps=10
    y_stop=Noysteps
else:
    Noysteps = round((y_stop-y_start)/y_step + 1)

#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = -20#0.4#log10(780e-9)
z_stop = -1#0.5#-5
z_step = 1#0.1#-5-log10(780e-9)
if zvarname == 'nothing':
    z_start=1
    Nozsteps=10
    z_stop = Nozsteps
else:
    Nozsteps = abs(round((z_stop-z_start)/z_step) + 1)


#set fixed values (prototype of frequency_trace_routines.py)
set_fixed_values(yvarname,
                 zvarname,
                 RF_start_fixed,
                 RF_stop_fixed,
                 vgatefine_fixed = 0,
                 vgate_fixed = 0.2,
                 vbias_fixed=0.006,
                 RF_voltage= 1,
                 RF_power=-70,
                 RFgate_power=-15,
                 LO_frequency= 2043,  #6997.0,
                 logtimeconstant = -4, #-6 has maximised noise value..
                 Vdd_fixed = 0.4,
                 Vattplus= 0,
                 Vattctrl= 0)

'''
all values should be in Voltage or dBm, logtimeconstant is
log10(780e-9) #minimum: 780ns ~ 10**(-6.1)
        timeconstant = 10**logtimeconstant
'''

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
    HFlockin.set_input_range0(0.001) #V 0.02
    HFlockin.set_input_range1(1) #V
    HFlockin.set_impedance50Ohm0(True)
    HFlockin.set_external_clock(False)
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
            data.add_value('DC (A)')
        else:
            data.add_value('R (V)')
            data.add_value('theta (rad)')
            data.add_value('X (V)')
            data.add_value('Y (V)')
            data.add_value('DC (A)')
            data.add_value('Temperature')
    elif readoutmode == 'LFlockin':
        data.add_value('R (A)')
        data.add_value('theta (rad)')
        data.add_value('X (A)')
        data.add_value('Y (A)')
        data.add_value('DC (A)')
        data.add_value('Temperature')
    elif (readoutmode == 'oscilloscope') | (readoutmode == 'HFoscil'):
        data.add_value('Channel 1 voltage (V)') #R
        data.add_value('Channel 2 voltage (V)') #pulse
        if recordxyoscil:
            data.add_value('Channel 3 voltage (V)') #X
            data.add_value('Channel 4 voltage (V)') #Y
            
        data.add_value('DC (A)')
        
data.create_file()
data.copy_file('frequency_trace_v03.py')
data.copy_file('frequency_trace_routines_v02.py')


#initialize spyview meta.txt file
#spyview_process(reset=True)

#create temporary meta file:
spyview_process(data,NoRFsteps,RF_start_fixed,RF_stop_fixed,Noysteps,y_stop,y_start,Nozsteps,z_start,z_stop)

#Actual sweep

for zvar in linspace(z_start,z_stop,Nozsteps):

    #set z variable
    sweep_vars(zvarname,zvar,sweepstep,sweeptime)
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    
    if (readoutmode == 'oscilloscope')|(readoutmode == 'HFoscil'):
        z_array=zvar*ones(Notimesteps)
    else:
        z_array=zvar*ones(NoRFsteps)   


    for yvar in linspace(y_start,y_stop,Noysteps):
        sweep_vars(yvarname,yvar,sweepstep,sweeptime)
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
        if (readoutmode == 'oscilloscope')|(readoutmode == 'HFoscil'):
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

        #qt.msleep(.1)
        #measure dc current    
        if recorddc:
            #i=vm.get_readval()/current_gain
            i = eval(vm.query('READ?'))/current_gain #a litte faster
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
                a_time= time()
                counter = 0
                for f in linspace(RF_start,RF_stop,NoRFsteps):
                    b_time= time()
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
                        kelvinA= tempcon.get_kelvinA()
                        kelvin_array=kelvinA*ones(NoRFsteps)
                        data.add_data_point(time_array, RF_array_fixed,y_array,amplitude_array,amplitude2_array,i_array,kelvin_array)
                        print 'oscilloscope...'
                        data.new_block()
                    elif readoutmode == 'HFoscil':
                        
                        #mytemperature=data.add_value('Temperature')
                        qt.msleep(0.2)#settlingtime)
                        
                        time_array, amplitude_array = HFoscil.get_trace(1)
                        time2_array, amplitude2_array = HFoscil.get_trace(2)

                        if recordxyoscil:
                            time3_array, amplitude3_array = HFoscil.get_trace(3)
                            time4_array, amplitude4_array = HFoscil.get_trace(4)

                        kelvinA= tempcon.get_kelvinA()
                        kelvin_array=kelvinA*ones(NoRFsteps)
                        if recordxyoscil:
                            data.add_data_point(time_array, RF_array_fixed,y_array,amplitude_array,amplitude2_array,amplitude3_array,amplitude4_array,i_array,kelvin_array)
                            print'recordxy loop'
                        else:
                            data.add_data_point(time_array, RF_array_fixed,y_array,amplitude_array,amplitude2_array,i_array,kelvin_array)
                        data.new_block()
                        #print amplitude_array[1]
                        #HFoscil.stop()
                        #HFoscil.run()
                    d_time= time()
                    if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                        print 'RF frequency: %sMHz' % f
                        
                    if scalarsubtractbackground & (yvarname != 'vgate'):
                        r_subtracted = r-r_ref

                    if recorddceachpoint:
                        if readoutmode == 'oscilloscope':
                            #i_array=vm.get_readval()/current_gain*ones(len(time_array))
                            i_array=eval(vm.query('READ?'))/current_gain*ones(len(time_array))
                        else:
                            #i_array[counter] = vm.get_readval()/current_gain
                            i_array[counter] = eval(vm.query('READ?'))/current_gain
                    counter=counter+1
                    f_time= time()
    
        if (readoutmode == 'oscilloscope')|(readoutmode == 'HFoscil'):
            spyview_process(data,NoRFsteps,min(time_array),min(time_array),Noysteps,y_stop,y_start,Nozsteps,z_start,zvar)
                

        g_time= time()
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
                print 'spectrum_analyser'
                data.add_data_point(RF_array_fixed,y_array,z_array,power,i_array)
            elif readoutmode == 'none':
                data.add_data_point(RF_array_fixed,y_array,z_array,i_array)
                print 'readoutmode == none'
            else:
                if scalarsubtractbackground & (yvarname != 'vgate'):
                    print 'scalarsub'
                    data.add_data_point(RF_array_fixed,y_array,z_array,r_subtracted,r_ref,r,theta,x,y,i_array)
                else:
                    kelvinA= tempcon.get_kelvinA()
                    kelvin_array=kelvinA*ones(NoRFsteps)
                    data.add_data_point(RF_array_fixed,y_array,z_array,r,theta,x,y,i_array,kelvin_array)

            data.new_block()
            
        h_time= time()
        if displayintermediatetime:
            xloop_tdiff = time()-inttime
            exp_time = xloop_tdiff*Noysteps*Nozsteps + (Noysteps+Nozsteps)*0.020
            inttime = time()
            print 'Estimated end:', localtime(begintime+exp_time)[2],'-',localtime(begintime+exp_time)[1],'-',localtime(begintime+exp_time)[0],' ',localtime(begintime+exp_time)[3], ':', localtime(begintime+exp_time)[4], ':', localtime(begintime+exp_time)[5]

    if (readoutmode != 'oscilloscope') & (readoutmode != 'HFoscil'):
        spyview_process(data,NoRFsteps,RF_start_fixed,RF_stop_fixed,Noysteps,y_stop,y_start,Nozsteps,z_start,zvar)
        #spyview_process(data,RF_start,RF_stop,y_start,y_stop,zvar)    
    

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
