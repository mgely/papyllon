import qt
import sys
from time import time,localtime
import numpy
from inspect import getfile, currentframe
execfile('frequency_trace_routines_v02.py')

filename = 'Ringdown_pow_set3'
begintime = time() #for measurement time calculation
inttime = time()
recorddc=True #also record dc current?
recorddceachpoint = True
#forwardandreverse=False #sweep forward and reverse?
highfrequency = True #measure with HFlockin (Zurich Instruments) and use HEMT (set Vdd)?
returntozero = True #sweep voltages back to zero?
displayintermediatetime=True
recordxyoscil=True
IVVIactivate = False #set this to False if no IVVI rack is available then it will use the lockins to send the voltages.
drivemode = 'external_mixer'
useattenuators = False
dualsmb = True
dfreq = 7.004 #MHz
external_lock = True # if false it simply uses the dfreq and sets itself to internal
'''
drivemode:
'direct_gate': use signal generator on gate, measure at drive frequency,
'external_mixer': use smbgate signal generator and externally mixed with lockin ref out,
'''
mixed_drivemode = (drivemode=='external_mixer')|(drivemode=='two-source')|(drivemode=='AM_gate')
direct_drivemode = (drivemode=='direct_source')|(drivemode=='direct_gate')
readoutmode = 'HFoscil'     #'HFlockin','HFoscil'
externality = 'RFswitch'    #'nothing','RFswitch',

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#install drivers with given settings (prototype of frequency_trace_routines.py )
install_drivers(instlist,
                readoutmode,
                highfrequency,
                externality,
                IVVIactivate)
#measurement information
temperature = tempcon.get_kelvinA()
med.set_temperature(temperature)
device = 'lg-04UR21c6'
med.set_device(device)
med.set_setup('1K dipstick')
med.set_user('Ben')
current_gain = 10e7 #10M V/A output to Amps
med.set_current_gain(current_gain)

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)


#set frequencies
RF_start_fixed=302.2# 303-5#295.7 -(1.92/2)#prev. 279-30 #MHz #res 1 at 136Mhz 2 at 306MHz
RF_stop_fixed =303.2# 303+5#295.7 +(1.92/2) #get just enough for the dc component #prev. 279+30 #MHz
RF_step=0.0125#0.4 #MHz
NoRFsteps = abs(int(RF_stop_fixed-RF_start_fixed)/RF_step) + 1
RF_center = (RF_start_fixed+RF_stop_fixed)/2.0

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2

coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','vbias':'Bias voltage (V)','RF_voltage':'RF voltage (V)','RF_power':'RF power (dBm)', 'RFgate_power':'RF gate power (dBm)', 'f_LO':'LO frequency (kHz)','vdd':'Vdd (V)','tc': 'Logarithm of time constant (log (s))','sweepdirection':'Sweep direction','Vattplus':'Attenuator Voltage+ (V)','Vattctrl':'Attenuator Control Voltage (V)','nothing':'Nothing'}

#set y variable
yvarname = 'vgate' # 'vgate' or 'RF_power' or 'f_LO' or 'vdd' or 'tc' or 'RFgate_power'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 0.66#0.774-0.05#0.787 - 0.2#0.787 - 0.017
y_stop  = 0.91#0.774+0.05#0.787 + 0.1#0.787 + 0.017
y_step  = 0.0125
if yvarname == 'nothing':
    y_start=1
    Noysteps=1
    y_stop=Noysteps
else:
    Noysteps = abs(int((y_stop-y_start)/y_step)) + 1

#set z variable #not usable yet as it would result in a 4d-data-cube..
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = -0.012#0.35#0.4#log10(780e-9)
z_stop = 0.012#0.47#0.5#-5
z_step = 0.002#0.01#0.1#-5-log10(780e-9)
if zvarname == 'nothing':
    z_start=1
    Nozsteps=1
    z_stop = Nozsteps
else:
    Nozsteps = abs(int((z_stop-z_start)/z_step)) + 1


#set fixed values (prototype of frequency_trace_routines.py)
set_fixed_values(yvarname,
                 zvarname,
                 RF_start_fixed,
                 RF_stop_fixed,
                 vgatefine_fixed = 0,
                 vgate_fixed = 0.66, #peak value for +3dBm power
                 vbias_fixed=0.0035, #high bias might be driving the tube (carefull!)
                 RF_voltage= 0,#0.15 was good
                 RF_power=-8,#3, #driving signal
                 RFgate_power=-10,#-13, #sideband signal
                 LO_frequency= 7004,  #6997.0,
                 logtimeconstant = log10(1.5e-6), #1.2us  -6.1,#10us timeconstant #-3, #-6 has maximised noise value..
                 Vdd_fixed = 0.4,
                 Vattplus= 0,
                 Vattctrl= 0)

#set oscilloscope numer of points
Notimesteps = 1000 #how many points in trace
scale = 3600 # scale of the lockin output for X,Y,R,Theta
settlingtime = 0.1 #10*timeconstant #overwrite settlingtime (instead of *10 try *1)
averaging_time = 2 # Yes take 1m to average on each point!
pulse_period =2143#1437#7#237 #us
pulse_width = 143#7#43 #us
HFoscil.set_time_scale(40e-6) #sec/div
filterorder = 8 #slowest decay > less dips.. #use 6dB/Oct Fastest decay with time..
print 'Averaging time: ',averaging_time
print 'pulse period: ',pulse_period
print 'pulse width: ',pulse_width
print 'est. req. time: ', float(averaging_time*NoRFsteps*Noysteps)/float(3600)
'''
all values should be in Voltage or dBm, logtimeconstant is
log10(780e-9) #minimum: 780ns ~ 10**(-6.1)
        timeconstant = 10**logtimeconstant
'''

#set gate voltage to measure background signal
vgate_ref = 0 #V

#set filename
#filename=device+'_'+drivemode+'_'+readoutmode+'_vs_'+yvarname
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgatefine()

#ready vm
vm.set_ben_settings(nplc=5)

#ready the HF oscilloscope
HFoscil.set_record_length(Notimesteps)
#HFoscil.set_autoscale(2)
HFoscil.set_ben_settings() #Set Highres 32bit mode and only transmit yValues not time values
HFoscil.set_average(2,1000000) #activate 10x averaging for chnel 2
HFoscil.set_average(3,1000000) #chnel 3
HFoscil.clear_buffer()

#ready the high-frequency lockin
if external_lock:
    HFlockin.set_reference('Signal Input 2')
else:
    HFlockin.set_reference('Internal')
HFlockin.set_output_switch0(1) #0 = Signal Output 1, 1 = Signal Output 2
HFlockin.set_input_range0(0.05) #V 0.02
HFlockin.set_input_range1(0.03) #V
HFlockin.set_impedance50Ohm0(True)
HFlockin.set_external_clock(True)
#filterorder = 2 #18db/oct #8 use 48dB/Oct
HFlockin.set_filter_order0(filterorder)
if external_lock:
    HFlockin.set_output_switch0(False) 
    HFlockin.set_output_switch1(False)
HFlockin.set_auxscale(0,scale)
HFlockin.set_auxscale(1,scale)
#ready the smbs
smbgate.set_RF_state(True)
smbgate.get_all()
smb.set_reference('INT')
smbgate.set_reference('EXT')
smb.set_pulse_period(pulse_period) #us
smb.set_pulse_width(pulse_width) #us
smb.set_pulse_state(False)
if dualsmb:
    smb.set_RF_state(True)

    
#ready datafile
data = qt.Data(name=filename)
data.add_coordinate('Time (s)') #X
data.add_coordinate('RF frequency (MHz)') #Y
data.add_coordinate(coordinate_names[yvarname]) #Z
#data.add_coordinate(coordinate_names[zvarname]) # for now data is limited to 3-D data cubes..
data.add_value(' X [V]') #X
data.add_value(' Y [V]') #Y
data.add_value(' (R [V])^2') #R
data.add_value(' Theta [rad])') #R
data.add_value(' DC [A]')
#data.add_value('Pulse [V]') #pulse
#data.add_value('Temperature')

#make copy of file       
data.create_file(name=filename, datadirs='D:\\data\\Ben\\')
scriptname = getfile(currentframe())
data.copy_file(scriptname)
data.copy_file('frequency_trace_routines_v02.py')

#create temporary meta file:
#ch2=HFoscil.get_trace(2) #take one trace to get generic numbers()
header = HFoscil.get_header(2,1) #chnel 2, wave 1
time_array = linspace(header[0],header[1],header[2])
spyview_process(data,
                header[2], #num of points
                header[0], #start
                header[1], #stop
                NoRFsteps,
                RF_stop_fixed,
                RF_start_fixed,
                Noysteps,
                y_start,
                y_stop)

#prepare sweep timers
loop2_start = time()
loop2_stop = time()
loop1_time = time()
osread_time = time()

#autocalibrate channels
#HFoscil.calibrate(1)
#qt.msleep(1)

#Actual sweep
for zvar in linspace(z_start,z_stop,Nozsteps):

    #set z variable
    sweep_vars(zvarname,zvar,sweepstep,sweeptime)
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    
    z_array=zvar*ones(Notimesteps)

    for yvar in linspace(y_start,y_stop,Noysteps):
        sweep_vars(yvarname,yvar,sweepstep,sweeptime)
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
        
        qt.msleep(0.005)
        yvar_array = yvar*ones(Notimesteps) #y-axis
        x_array=ones(Notimesteps)
        y_array=ones(Notimesteps)
        r_array=ones(Notimesteps)
        theta_array=ones(Notimesteps)
        pulse_array=ones(Notimesteps)
        
        #measure temperature
        kelvinA= tempcon.get_kelvinA()
        kelvin_array=kelvinA*ones(Notimesteps)

        loop2_start= time()
        counter = 0

        print 'Sweep RF'
        for f in linspace(RF_start,RF_stop,NoRFsteps):
            #step frequency
            if dualsmb:
                smb.set_RF_frequency(f)
            smbgate.set_RF_frequency(f+dfreq)
            vm.write('INIT') #tell keithley to start measuring while reading out the other devices.
            qt.msleep(settlingtime)
            RF_array_fixed=f*ones(Notimesteps)
            HFoscil.clear_buffer() #clear buffer and start averaging
            osread_time = time()
            qt.msleep(averaging_time) #average time per point
            ch2 = HFoscil.get_trace(2,Notimesteps) #X values
            ch3 = HFoscil.get_trace(3,Notimesteps) #Y values
            #remove offset(take point after a long time and def. that as zero) and rescale it
            #r_array = (ch2-ch2.min())/scale
            x_array = (ch2)/scale
            y_array = (ch3)/scale

	    if abs(y_array.max()) > abs(y_array.min()):
		    y_sub = y_array.min()
	    else:
		    y_sub = y_array.max()
	    if abs(x_array.max()) > abs(x_array.min()):
		    x_sub = x_array.min()
	    else:
		    x_sub = x_array.max()
            y2_array = y_array-y_sub
            x2_array = x_array-x_sub
            #remove zeros for theta devision:
            nn = 0
            for i in x2_array:
                if i == 0:
                    x2_array[nn]=x2_array[nn-1] #find and change zeros from x2_array
                nn+=1
            rpower_array = x2_array**2+y2_array**2
            theta_array = arctan(y2_array/x2_array) #in radians
	    
            #get DC value per point in RF and Y
            i_array = (eval(vm.query('FETCH?'))/current_gain)*ones(Notimesteps)
            osread_time = time()-osread_time


            
            data.add_data_point(time_array,       #time axis
                                RF_array_fixed, #RF frequency
                                yvar_array,     #y-axis (gate,...)
                                x_array,        #X
                                y_array,        #Y value
                                rpower_array,        #R
                                theta_array,    #Theta
                                i_array,        #DC value
                                #pulse_array     #pulse
                                #kelvin_array,
                                )

            #check length:
            #len(time_array),len(RF_array_fixed),len(y_array)
            #len(ch2), len(ch3), len(R_array), len(Theta_array)
            #len(i_array), len(kelvin_array), len(ch1)
            
            data.new_block()


            loop1_time = loop1_time - time()
            if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                print 'RF frequency: %sMHz' % f
                print 'HF-Oscilloscope-readtime:', osread_time, '\n Looptime:', loop1_time, '\n avg time pp:', (time()-loop2_start)/(counter+1)
            loop1_time = time()
            counter=counter+1
        
        loop2_end= time()
        spyview_process(data,
                header[2],
                header[0],
                header[1],
                NoRFsteps,
                RF_stop_fixed,
                RF_start_fixed,
                Noysteps,
                y_start,
                y_stop)
        
        if displayintermediatetime:
            xloop_tdiff = time()-inttime
            exp_time = xloop_tdiff*Noysteps*Nozsteps + (Noysteps+Nozsteps)*0.020
            inttime = time()
            print 'Estimated end:', localtime(begintime+exp_time)[2],'-',localtime(begintime+exp_time)[1],'-',localtime(begintime+exp_time)[0],' ',localtime(begintime+exp_time)[3], ':', localtime(begintime+exp_time)[4], ':', localtime(begintime+exp_time)[5]

#reset voltages
ramp(vi,'vgatefine',0,sweepstep,sweeptime)
ramp(vi,'vgate',0,sweepstep,sweeptime)
ramp(vi,'vbias',0,sweepstep,sweeptime)
ramp(vi,'vdd',0,sweepstep,sweeptime)
#if externality == 'RFswitch':
#    vi.set_vRFplus(0)
#    vi.set_vRFminus(0)

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
vm.set_trigger_continuous(True)

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring
data.close_file()
qt.mend()
