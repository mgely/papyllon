# -*- coding: cp1252 -*-
import qt
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen3D_ben.py')

begintime = time()
usefinegate = False
returntozero = True
measurevoltage = False
measurecontvoltage = False
measuretemperature = True
usebuffer = False #Make use of the Keithley 2700 buffer)

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')
if 'HFlockin' not in instlist:
    HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)

if False|('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    HFlockin.set_auxmode(2,-1)  #sets aux 3 to manual
    HFlockin.set_auxmode(3,-1)  #sets aux 4 to manual
    vi.add_variable_scaled('vgate',HFlockin,'auxoffset2',1,0.0)
    vi.add_variable_scaled('vbias',HFlockin,'auxoffset3',5,0.0) #with the 10 to 1 vdivider 9.253*100 10mV/1V 1V/10V -> 10mV/10V
    vi.add_variable_scaled('vgatefine',lockin,'out2',10,0.0) #0.1x modulation
    vi.add_variable_scaled('vdd',lockin,'out1',1,0.0)
    '''
    #Lockin aux: The range is -10.5V to +10.5V and the resolution is 1 mV max 10mA(input has 16bit & 1/3mV resol.).
    '''
if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med',reset=True)

    
if measuretemperature:
    if 'tempcon' not in instlist:
        tempcon = qt.instruments.create('tempcon','Lakeshore_331',address='GPIB::12')    

if measuretemperature:
    temperature = tempcon.get_kelvinA()
else:
    temperature = 300
#measurement information
med.set_temperature(temperature)
device = 'lg-04UR21c6'
med.set_device(device)
med.set_setup('1K dipstick')
med.set_user('Ben')
#current_gain = 0.001 #GV/A=mV/pA
#current_gain = current_gain*-1e3 # multiplier used to devide the measured voltage.
current_gain = 10**6 #1M V/A (setting on the measurement unit)
med.set_current_gain(current_gain)
coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','vbias':'Bias voltage (V)','vdd':'vdd (V)','nothing':'Nothing'}

# voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms, this does not affect measurement speed)
# measurement times
zvalsleep = 0.5 # time to wait afer setting the value before doing y sweep
yvalsleep = 0.4 # time to wait after setting the value before doing x sweep
xvalsleep = 0.0 # time to wait between set values and measurement
vm.set_nplc(1) #sets measuremnt time to n powerline cycle by keithley  1 = 20ms
#next two vals only when using the buffer.
buffersleep = 0.022 # qt.msleep(0.022) @ plc = 1 is optimum
speeder = 3 # How many measurements per request (lower inc sync, higher inc speed)

#set x variable
xvarname = 'vbias' # 'vgate' or 'RF_power' or 'f_LO' or 'vdd' or 'tc' vbias
if xvarname not in coordinate_names:
    sys.exit('Aborted: xvarname not in coordinate_names')
x_start = -0.01
x_stop =   0.01
x_step =   0.0001
if xvarname == 'nothing':
    x_stop=0
    x_start=1
    Noxsteps=1
else:
    Noxsteps = round((x_stop-x_start)/x_step + 1)


#set y variable
yvarname = 'vgate' # 'vgate' or 'RF_power' or 'f_LO' or 'vdd' or 'tc' vbias
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = -2
y_stop = 2
y_step = 0.001
if yvarname == 'nothing':
    y_stop=y_start
    Noysteps=1
else:
    Noysteps = round((y_stop-y_start)/y_step + 1)


#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'vdd' or 'tc' vbias
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = -6
z_stop = -2
z_step = 1
if zvarname == 'nothing':
    z_start=1
    Nozsteps=1
    z_stop = Nozsteps
else:
    Nozsteps = abs(round((z_stop-z_start)/z_step) + 1)

#set fixed values
if (xvarname != 'vgatefine') & (yvarname != 'vgatefine') & (zvarname != 'vgatefine'):
    vgatefine_fixed = 0 #V
    ramp(vi,'vgatefine',vgatefine_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage offset: %sV +++' % vgatefine_fixed

if (xvarname != 'vgate') & (yvarname != 'vgate') & (zvarname != 'vgate'):
    vgate_fixed = 0 #V
    vgate=vgate_fixed
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if (xvarname != 'vbias') & (yvarname != 'vbias') & (zvarname != 'vbias'):
    vbias_fixed=0.005 #V
    ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
    print '+++ Bias voltage: %sV +++' % vbias_fixed    

if (xvarname != 'vdd') & (yvarname != 'vdd') & (zvarname != 'vdd'):
    vdd_fixed = 0 # 1 V
    ramp(vi,'vdd',vdd_fixed,sweepstep,sweeptime)
    print '+++ vdd: %sV +++' % vdd_fixed

#ready vm
vm.set_display(0)                               #turn display off
vm.write('*RST')
vm.write('SENSe:FUNCtion "VOLTage:DC"')
vm.write(':FORM:ELEM READ') #just getting the values not all that crap... :)
vm.write('INITiate:CONTinuous OFF;:ABORt')      #vm.set_trigger_continuous(False)
vm.write('SYSTem:AZERo:STATe ON')               #Turn autozero off for speed (will result in voltage offsets over time!!)
vm.write('SENSe:VOLTage:DC:AVERage:STATe OFF')  #Turn off filter for speed
vm.write('SENSe:VOLTage:DC:RANGe 1')          #give it a fixed range to max speed
vm.write('TRIG:DEL:AUTO OFF')                   #set triger delay to manual
vm.write('TRIG:DEL 0')                          #TRIGger:DELay to 0 sec
vm.write('TRIGger:COUNt 1')
vm.get_all()

#datafile
filename=device+'-ND_dc_trace_'+xvarname+'_vs_'+yvarname+'_and_'+zvarname
data = qt.Data(name=filename)
data.add_coordinate(coordinate_names[xvarname])
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])
if measurevoltage:
    data.add_value('Voltage (V)')
    data.add_value('Temperature')
else:
    data.add_value('Current (A)')
    data.add_value('Temperature')
    
data.create_file()
data.copy_file('ND_dc_trace-NOIVVI.py')

#if usefinegate:
#    vgaterough = (vgate_stop+vgate_start)/2.0
#    ramp(vi,'vgate',vgaterough,sweepstep,sweeptime)

#define sweep-options (&prevent system from doing something upon mistyping..)

sweepvar = 0
'''
def rampvgatefine(sweepvar,sweepstep,sweeptime):
    ramp(vi,'vgatefine',sweepvar,sweepstep,sweeptime)
def rampvgate(sweepvar,sweepstep,sweeptime):
    ramp(vi,'vgate',sweepvar,sweepstep,sweeptime)
def rampvbias(zvar,sweepstep,sweeptime):
    ramp(vi,'vbias',sweepvar,sweepstep,sweeptime)
def rampvdd(sweepvar,sweepstep,sweeptime):
    ramp(vi,'vdd',sweepvar,sweepstep,sweeptime)

execfile('rampoptions.py')
rampoptions = {'vgatefine' : rampvgatefine ,
               'vgate' : rampvgate,
               'vbias' : rampvbias,
               'vdd' : rampvdd}
'''

#actual sweep
for zvar in linspace(z_start,z_stop,Nozsteps):
    
    
    #set z variable
    #if zvarname in rampoptions:
        #rampoptions[zvarname](zvar,sweepstep,sweeptime)
    if zvarname == 'vgatefine':
        ramp(vi,'vgatefine',zvar,sweepstep,sweeptime)
    elif zvarname == 'vgate':
        vgate = zvar
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'vbias':
        ramp(vi,'vbias',zvar,sweepstep,sweeptime)
    elif zvarname == 'Vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)        

    qt.msleep(zvalsleep)
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar
    
    for yvar in linspace(y_start,y_stop,Noysteps):

        #set y variable
        #if yvarname in rampoptions:
            #rampoptions[yvarname](yvar,sweepstep,sweeptime)
        if yvarname == 'vgatefine':
            ramp(vi,'vgatefine',yvar,sweepstep,sweeptime)
        elif yvarname == 'vgate':
            vgate = yvar
            ramp(vi,'vgate',yvar,sweepstep,sweeptime)
        elif yvarname == 'vbias':
            ramp(vi,'vbias',yvar,sweepstep,sweeptime)             
        elif yvarname == 'Vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)        

        qt.msleep(yvalsleep)
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
        counter = 0
        kelvinA = tempcon.get_kelvinA() #do temp measurement here so its not in the high freq. loop.
        if usebuffer:
            counter2 = 0
            buffersize = Noxsteps
            vm.write('TRAC:CLE') #clear old buffer
            vm.write('TRAC:POIN '+str(buffersize)) #set buffer size
            vm.write('TRAC:FEED SENS') #fill buffer with data points
            vm.write('TRAC:FEED:CONTROL NEXT') #activate buffer now fill buffer once then turn off again..
            vm.write('SAMP:COUN '+str(speeder)) #take only 1 data point per triger
            kelvin_array=kelvinA*ones(Noxsteps)

        for xvar in linspace(x_start,x_stop,Noxsteps):

            #set x variable
            #if xvarname in rampoptions:
            if xvarname == 'vgatefine':
                ramp(vi,'vgatefine',xvar,sweepstep,sweeptime)
            elif xvarname == 'vgate':
                vgate = xvar
                ramp(vi,'vgate',xvar,sweepstep,sweeptime)
            elif xvarname == 'vbias':
                ramp(vi,'vbias',xvar,sweepstep,sweeptime)             
            elif xvarname == 'Vdd':
                ramp(vi,'vdd',xvar,sweepstep,sweeptime)        

#                rampoptions[xvarname](xvar,sweepstep,sweeptime) #req. approx 6 sec for 500 points?
            qt.msleep(xvalsleep)
            
            if Noxsteps > 10: #print sweep number
                if counter%int(((x_stop-x_start)/x_step+1)/10)==0:
                    print coordinate_names[xvarname] + ': %s' % xvar
                counter=counter+1
        
            if measurevoltage:
                    i=vm.get_readval() #V
            elif measurecontvoltage:
                    i=vm.get_readnextval() #requires a triger or being set in cont mode, waits until value is ready
            elif usebuffer:
                    #vm.query('TRAC:DATA:SEL? 0, 5')
                    qt.msleep(buffersleep)# 29ms sleep required at plc=1 (ethernet cable and measurement seems not fast enough)
                    if counter2%speeder == 0: # attempt to minimize bandwidth
                        buffstatus = int(vm.query('TRAC:NEXT?'))
                        if counter2 - buffstatus > 0:
                            qt.msleep(0.04)
                            print counter2
                        if counter2 - buffstatus <0:
                            print counter2 - buffstatur
                            print 'to slow'
                        vm.write('INIT') #send a triger to measure one cycle of data points
                        
                    counter2 = counter2 +1
                    
            else:
                    i = eval(vm.query('READ?'))/current_gain
                    #i = vm.trigfetch()/current_gain #catch data point
                    #i=vm.get_readval()/current_gain
                    data.add_data_point(xvar,yvar,zvar,i,kelvinA) #requires virtually no extra time..

        if usebuffer:
            qt.msleep(0.04)
            i_array = vm.query('TRAC:DATA:SEL? 0, '+str(buffersize))

            i_array = np.array(eval(i_array))/current_gain
            xvar_array= np.array(linspace(x_start,x_stop,Noxsteps))
            yvar_array=yvar*ones(Noxsteps)
            zvar_array=zvar*ones(Noxsteps)
                                 
            data.add_data_point(xvar_array,yvar_array,zvar_array,i_array,kelvin_array)
        
        data.new_block()
        spyview_process(data,Noxsteps,x_start,x_stop,Noysteps,y_stop,y_start,Nozsteps,z_start,zvar)    
    
#generate plot, disturbs timing
#plot2d = qt.Plot2D(data, name='measure2D',coorddim=0, valdim=3)
#plot2d.save_png(filepath=data.get_dir()+'\\'+'plot.png')

#reset voltages
if returntozero:
    ramp_all_to_zero(vi,sweepstep,sweeptime)
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)
    ramp(vi,'vdd',0,sweepstep,sweeptime)

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int(1/3600*(endtime-begintime)),"m":int(1/60*(endtime-begintime)),"s":int(1*(endtime-begintime))}
print 'Measurement time: '+ measurementtimestring

#reset voltage measurement
vm.set_trigger_continuous(True)
vm.set_display(1) 

data.close_file()

qt.mend()



