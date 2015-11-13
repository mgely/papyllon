import qt
import sys
from time import time,localtime
from inspect import getfile, currentframe
import numpy
#execfile('ramp.py') included in frequency_trace_routines.py
#execfile('metagen3D_ben.py') included in frequency_trace_routines.py
execfile('frequency_trace_routines_v02.py')
def average(s): return sum(s) * 1.0/ len(s)
def stddev(s): return sqrt(average(map(lambda x: (x-average(s))**2,s)))

filename = 'HFlockin-sweep'
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
externality = 'RFswitch' #'nothing'
#'RFswitch','attenuator' (not programmed yet), 'nothing' 

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#install drivers with given settings (prototype of frequency_trace_routines.py )
install_drivers(instlist,
                readoutmode,
                highfrequency,
                externality,
                IVVIactivate)

temperature = tempcon.get_kelvinA()
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
RF_start_fixed=298.5#305#1.5#302.05#prev. 279-30 #MHz #res 1 at 136Mhz 2 at 306MHz
RF_stop_fixed =300.75#310.5#3.5#302.7 #prev. 279+30 #MHz
RF_step=0.01#01#0.002#0.4 #MHz
NoRFsteps = int(abs(RF_stop_fixed-RF_start_fixed)/RF_step) + 1
RF_center = (RF_start_fixed+RF_stop_fixed)/2.0
RF_array_fixed = linspace(RF_start_fixed,RF_stop_fixed,NoRFsteps)

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2

coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','vbias':'Bias voltage (V)','RF_voltage':'RF voltage (V)','RF_power':'RF power (dBm)', 'RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','vdd':'Vdd (V)','tc': 'Logarithm of time constant (log (s))','sweepdirection':'Sweep direction','Vattplus':'Attenuator Voltage+ (V)','Vattctrl':'Attenuator Control Voltage (V)','nothing':'Nothing'}

#set y variable
yvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'vdd' or 'tc' or 'RFgate_power'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start=0.4-0.02#0.78-0.015 
y_stop =0.4+0.02#0.78+0.015 
y_step =0.001#0.0005
if yvarname == 'nothing':
    y_start=1
    Noysteps=50
    y_stop=Noysteps
else:
    Noysteps = int(abs((y_stop-y_start)/y_step)) + 1

#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start= 0.003#0.35#0.4#log10(780e-9)
z_stop = 0.012#0.47#0.5#-5
z_step = 0.0005#0.01#0.1#-5-log10(780e-9)
if zvarname == 'nothing':
    z_start=1
    Nozsteps=1
    z_stop = Nozsteps
else:
    Nozsteps = abs(int((z_stop-z_start)/z_step)) + 1

LO_frequency= float(7004)  #6997.0,y
#set fixed values (prototype of frequency_trace_routines.py)
set_fixed_values(yvarname,
                 zvarname,
                 RF_start_fixed,
                 RF_stop_fixed,
                 vgatefine_fixed = 0,
                 vgate_fixed = 0.4,#768,
                 vbias_fixed=-0.005,
                 RF_voltage= 0,#0.15 was good
                 RF_power=-20,#30,
                 RFgate_power=-8,
                 LO_frequency= LO_frequency,  #6997.0,
                 logtimeconstant = -2,#1us timeconstant #-3, #-6 has maximised noise value..
                 Vdd_fixed = 0.4,
                 Vattplus= 0,
                 Vattctrl= 0)

settlingtime = 0.001 + 2*timeconstant #overwrite settlingtime (instead of *10 try *1)
filterorder = 8 #18db/oct #8 use 48dB/Oct
scale = 7000
pulse_period = 1000000#1437#7#237 #us
pulse_width  = 1000000#7#43 #us
RF_start = RF_start_fixed #not returning this via prototype yet
RF_stop = RF_stop_fixed
'''
all values should be in Voltage or dBm, logtimeconstant is
log10(780e-9) #minimum: 780ns ~ 10**(-6.1)
        timeconstant = 10**logtimeconstant
'''

#set gate voltage to measure background signal
vgate_ref = 0 #V
vi.set_vRFplus(5)
vi.set_vRFminus(-5)    

qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgatefine()

#ready vm
vm.write('*RST')
vm.set_nplc(1) #sets measuremnt time to n powerline cycle by keithley  1 = 20ms
vm.set_display(0)                               #turn display off
vm.write('SENSe:FUNCtion "VOLTage:DC"')
vm.write(':FORM:ELEM READ') #just getting the values nothing else.. :)
vm.write('INITiate:CONTinuous OFF;:ABORt')      #vm.set_trigger_continuous(False)
vm.write('SYSTem:AZERo:STATe OFF')               #Turn autozero off for speed (will result in voltage offsets over time!!)
vm.write('SENSe:VOLTage:DC:AVERage:STATe OFF')  #Turn off filter for speed
vm.write('SENSe:VOLTage:DC:RANGe 1')          #give it a fixed range to max speed
vm.write('TRIG:DEL:AUTO OFF')                   #set triger delay to manual
vm.write('TRIG:DEL 0')                          #TRIGger:DELay to 0 sec
vm.write('TRIGger:COUNt 1')
vm.get_all()

#ready the high-frequency lockin
if (readoutmode == 'HFlockin') | (readoutmode == 'oscilloscope') | (readoutmode == 'HFoscil'):
    #HFlockin.set_reference('Internal')
    HFlockin.set_reference('Signal Input 2')
    HFlockin.set_output_switch0(1) #0 = Signal Output 1, 1 = Signal Output 2
    HFlockin.set_input_range0(0.04) #V 0.02
    HFlockin.set_input_range1(0.02) #V
    HFlockin.set_impedance50Ohm0(True)
    #filterorder = 1 #use 6dB/Oct
    HFlockin.set_filter_order0(filterorder)
    HFlockin.set_output_switch0(False)
    HFlockin.set_output_switch1(False)
    HFlockin.set_auxscale(0,scale)
    HFlockin.set_auxscale(1,scale)
    HFlockin.set_external_clock(False)
    #HFlockin.set_external_clock(True)

#ready the smb
smbgate.set_RF_state(True)
smbgate.get_all()
smb.set_reference('INT')
smbgate.set_reference('EXT')
smb.set_pulse_period(pulse_period) #us
smb.set_pulse_width(pulse_width) #us
smb.set_pulse_state(False)
smb.set_RF_state(True)
smbgate.get_all()
smb.get_all()

#Set up datafile
data = qt.Data(name=filename)
data.create_file(name=filename, datadirs='D:\\data\\Ben\\')
scriptname = getfile(currentframe())
data.copy_file(scriptname)
data.copy_file('frequency_trace_routines_v02.py')

data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])
data.add_value('R (Vrms/sqrt(Hz))')
data.add_value('theta ((radrms/sqrt(Hz))')                        
data.add_value('X (Vrms/sqrt(Hz))')
data.add_value('Y (Vrms/sqrt(Hz))')
data.add_value('DC (A)')                              
data.add_value('Temperature')            

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

        x=zeros(NoRFsteps)
        y=zeros(NoRFsteps)
        r=zeros(NoRFsteps)
        theta=zeros(NoRFsteps)
        power=zeros(NoRFsteps)
        #qt.msleep(.05)
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

            #ramp(vi,'vgate',vg,sweepstep,sweeptime)
            #print '^^^Gate voltage: %s ^^^' % vg
            
            

	    a_time= time()
	    counter = 0
	    for f in linspace(RF_start,RF_stop,NoRFsteps):

	        b_time= time()
	        smbgate.set_RF_frequency(f+LO_frequency/1000)
	        smb.set_RF_frequency(f)
	        qt.msleep(settlingtime)
	        #if recorddceachpoint:
	    	#	vm.write('INIT') #tell keithley to start measuring while reading out the other devices.

	        if recorddceachpoint:
	    		i_array[counter] = eval(vm.query('READ?'))/current_gain

	        x[counter]=HFlockin.get_x()
	        y[counter]=HFlockin.get_y()
	        r[counter]=HFlockin.get_amplitude()
	        theta[counter] = HFlockin.get_phase()
	        d_time= time()
	        if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
	    		print 'RF frequency: %sMHz' % f

	        counter=counter+1
	        f_time= time()
    
        g_time= time()
        #save data
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

    spyview_process(data,NoRFsteps,RF_start_fixed,RF_stop_fixed,Noysteps,y_stop,y_start,Nozsteps,z_start,zvar)
    

#plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
#plot2dx.add_data(data, coorddim=0, valdim=4)
#plot2dx.update
#if (readoutmode != 'oscilloscope') & (readoutmode != 'HFoscil'):    
#    plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)
#    plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
#    plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')
#    #plot2dc = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=7)
#    #plot2dc.save_png(filepath=data.get_dir()+'\\'+'plot2dc.png')

#reset voltages
if returntozero:
    ramp(vi,'vgatefine',0,sweepstep,sweeptime)
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)
    ramp(vi,'vdd',0,sweepstep,sweeptime)
    if useattenuators:
        vi.set_vattplus(0)
        vi.set_vattctrl(0)
    if externality == 'RFswitch':
        vi.set_vRFplus(5)
        vi.set_vRFminus(-5)

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
smbgate.set_RF_state(False)
smb.set_RF_state(False)
data.close_file()

qt.mend()
