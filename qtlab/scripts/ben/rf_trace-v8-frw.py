import qt
from time import time, localtime, strftime
import numpy as np
from inspect import getfile, currentframe
execfile('ramp.py')
execfile('metagen3D_ben.py')
filename = 'RF-trace-frw'

begintime = time()
usefinegate = False
returntozero = True
measurevoltage = False
measuretemperature = True
timedebugging = False

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
    vi.add_variable_scaled('vbias',HFlockin,'auxoffset3',5*100,0.0) #with the 10 to 1 vdivider 9.253*100 10mV/1V 1V/10V -> 10mV/10V
    vi.add_variable_scaled('vgatefine',lockin,'out2',10,0.0) #0.1x modulation
    vi.add_variable_scaled('vdd',lockin,'out1',1,0.0)
    vi.add_variable_scaled('vRFplus',lockin,'out4',1,0.0)
    vi.add_variable_scaled('vRFminus',lockin,'out3',1,0.0)

    '''
    #Lockin aux: The range is -10.5V to +10.5V and the resolution is 1 mV max 10mA(input has 16bit & 1/3mV resol.).
    '''
if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if measurevoltage:
    if 'vm2' not in instlist:
        vm2 = qt.instruments.create('vm2','Keithley_2700',address='GPIB::16')

if 'med' not in instlist:
    med = qt.instruments.create('med','med',reset=True)
    
if measuretemperature:
    if 'tempcon' not in instlist:
        tempcon = qt.instruments.create('tempcon','Lakeshore_331',address='GPIB::12')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')



if measuretemperature:
    temperature = tempcon.get_kelvinA()
else:
    temperature = 3
#measurement information
med.set_temperature(temperature)
device = 'lg-04UR21c6'
med.set_device(device)
med.set_setup('1K dipstick')
med.set_user('Ben')
current_gain = 10**7 #1M V/A (setting on the measurement unit)
voltage_gain = 1
med.set_current_gain(current_gain)
coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','vbias':'Bias voltage (V)','vdd':'vdd (V)','nothing':'Nothing','RF_power':'RF_power','RF_frequency':'RF_frequency'}

# voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms, this does not affect measurement speed)
# measurement times
zvalsleep = 0.06 # time to wait afer setting the value before doing y sweep
yvalsleep = 0.06 # time to wait after setting the value before doing x sweep
xvalsleep = 0.0 # time to wait between set values and measurement

#set x variable
xvarname = 'RF_frequency' # 'vgate' or 'RF_power' or 'RF_frequency' or 'f_LO' or 'vdd' or 'tc' vbias
if xvarname not in coordinate_names:
    sys.exit('Aborted: xvarname not in coordinate_names')
x_start =302.05
x_stop = 302.7
x_step = 0.01
if xvarname == 'nothing':
    x_stop=0
    x_start=0.1
    Noxsteps=1
else:
    Noxsteps = int(abs((x_stop-x_start)/x_step)) +1


#set y variable
yvarname = 'vgate' # 'vgate' or 'RF_power' or 'RF_frequency' or 'f_LO' or 'vdd' or 'tc' vbias
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start =0.66#0.3#0.787 -0.017 #0.759
y_stop = 0.91#0.8#-17#0.787 +0.017 #0.797
y_step =  0.02
if yvarname == 'nothing':
    y_start= 0
    y_stop=  0.01
    Noysteps=1
else:
    Noysteps = int(abs((y_stop-y_start)/y_step)) +1


#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'RF_frequency' or 'f_LO' or 'vdd' or 'tc' vbias
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = 0
z_stop = 0.01
z_step = 0.01
if zvarname == 'nothing':
    z_start= 0
    z_stop = 0.01
    Nozsteps = 1
else:
    Nozsteps = int(abs((z_stop-z_start)/z_step)) +1

estimate_time=Noxsteps*Noysteps*Nozsteps*0.046/3600
print 'First time estimate: ', int(estimate_time),':',int((estimate_time%1)*60)

#set fixed values
if (xvarname != 'vgatefine') & (yvarname != 'vgatefine') & (zvarname != 'vgatefine'):
    vgatefine_fixed = 0 #-0.76 #V
    ramp(vi,'vgatefine',vgatefine_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage offset: %sV +++' % vgatefine_fixed

if (xvarname != 'vgate') & (yvarname != 'vgate') & (zvarname != 'vgate'):
    vgate_fixed = 0.774 #V
    vgate=vgate_fixed
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if (xvarname != 'vbias') & (yvarname != 'vbias') & (zvarname != 'vbias'):
    vbias_fixed=0.0005 #V
    ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
    print '+++ Bias voltage: %sV +++' % vbias_fixed    

if (xvarname != 'vdd') & (yvarname != 'vdd') & (zvarname != 'vdd'):
    vdd_fixed = 0 # 1 V
    ramp(vi,'vdd',vdd_fixed,sweepstep,sweeptime)
    print '+++ vdd: %sV +++' % vdd_fixed

if (xvarname != 'RF_power') & (yvarname != 'RF_power') & (zvarname != 'RF_power'):
    RF_power_fixed = -10#-7+10 #dbm
    smbgate.set_RF_power(RF_power_fixed)
    print '+++ RF_power: %sdBm +++' % RF_power_fixed

if (xvarname != 'RF_frequency') & (yvarname != 'RF_frequency') & (zvarname != 'RF_frequency'):
    RF_freq_fixed = 200 #MHz
    smbgate.set_RF_frequency(RF_freq_fixed)
    print '+++ RF_freq: %sMHz +++' % RF_freq_fixed

#Disable all sources turn SMBs off
if (xvarname == 'RF_frequency') or (yvarname == 'RF_frequency') or (zvarname == 'RF_frequency'):
    smbgate.set_RF_state(True)
    smbgate.write('POW:ALC:SONC') #activates the Power level control once only
    #smbgate.write('POW:ALC OFF')
else:
    smbgate.set_RF_state(False)
smb.set_RF_state(False)
HFlockin.set_output_switch0(False) 
HFlockin.set_output_switch1(False)

#ready vm
vm.set_ben_settings()
#ready vm2
if measurevoltage:
    vm2.set_ben_settings()


a_time=0
b_time=0
c_time=0
xx_time=0
xx2_time=0

#datafile
data = qt.Data(name=filename)
data.add_coordinate(coordinate_names[xvarname])
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])
if measurevoltage:
    data.add_value('Current (A)')
    data.add_value('Voltage (V)')
    data.add_value('Temperature')
else:
    data.add_value('Current (A)')
    data.add_value('Temperature')
    
#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Ben\\')
scriptname = getfile(currentframe())
data.copy_file(scriptname, subfolder = False)
print '-- data file created --'

#create predata file
spyview_process(data,Noxsteps,x_start,x_stop,Noysteps,y_stop,y_start,Nozsteps,z_start,z_stop)

#actual sweep
qt.mstart()
xloop_time = time()
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
    elif zvarname == 'vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)
    elif zvarname == 'RF_power':
        smbgate.set_RF_power(zvar)
    elif zvarname == 'RF_frequency':
        smbgate.set_RF_frequency(zvar)
        

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
        elif yvarname == 'vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)
        elif yvarname == 'RF_power':
            smbgate.set_RF_power(yvar)
            print 'set RF power'
        elif yvarname == 'RF_frequency':
            smbgate.set_RF_frequency(yvar)

        qt.msleep(yvalsleep)
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
        counter = 0
        kelvinA = tempcon.get_kelvinA() #do temp measurement here so its not in the high freq. loop.

        #Cal. approx required time for measurement
        xloop_tdiff= time()-xloop_time
        time_pp= float(xloop_tdiff)/float(Noxsteps)
        if timedebugging:
            print 'averaged_time_pp: ', time_pp
        exp_time = xloop_tdiff*Noysteps*Nozsteps #calculate how long the total measurement will take
        xloop_time = time()
        exp_finish = begintime+exp_time +(Noysteps+Nozsteps)*0.020
        print 'Estimated end:', localtime(begintime+exp_time)[2],'-',localtime(begintime+exp_time)[1],'-',localtime(begintime+exp_time)[0],' ',localtime(begintime+exp_time)[3], ':', localtime(begintime+exp_time)[4], ':', localtime(begintime+exp_time)[5]
        
        
        for xvar in linspace(x_start,x_stop,Noxsteps):
            #vm.write('INIT') #read while setting voltage, increases speed, looses sync better option is continuos mode.
            #set x variable
            xx_time=time()
            if xvarname == 'vgatefine':
                ramp(vi,'vgatefine',xvar,sweepstep,sweeptime)
            elif xvarname == 'vgate':
                vgate = xvar
                ramp(vi,'vgate',xvar,sweepstep,sweeptime)
            elif xvarname == 'vbias':
                ramp(vi,'vbias',xvar,sweepstep,sweeptime)             
            elif xvarname == 'vdd':
                ramp(vi,'vdd',xvar,sweepstep,sweeptime)
            elif xvarname == 'RF_power':
                smbgate.set_RF_power(xvar)
            elif xvarname == 'RF_frequency':
                smbgate.set_RF_frequency(xvar) #this is a little slower is also a get command to update qt lab..
            xx2_time=time()

            if Noxsteps > 5: #print sweep number
                if counter%int(((x_stop-x_start)/x_step+1)/1)==0:
                    aa_time = time()
                    if timedebugging:
                        print coordinate_names[xvarname] + ': %s' % xvar, 't_keithley: ',b_time-a_time,'t_write_data: ',c_time-b_time, 't_var: ',xx2_time-xx_time, 't_varleft:',xx_time-c_time
                    else:
                        print coordinate_names[xvarname] + ': %s' % xvar
                counter=counter+1
            if measurevoltage:
                    a_time=time() #time debugging code
                    vm2.write('INIT')
                    i=float(eval(vm.query('READ?')))/float(current_gain) #safer option as the other one is a little uncertain when its being recored
                    i2=float(eval(vm2.query('FETCH?')))/float(voltage_gain) #fetch the voltage value
                    b_time=time() #time debugging code
                    data.add_data_point(xvar,yvar,zvar,i,i2,kelvinA) #requires virtually no extra time..
                    c_time=time() #time debugging code
            else:
                    a_time=time() #time debugging code
                    i=float(eval(vm.query('READ?')))/float(current_gain) #safer option as the other one is a little uncertain when its being recored
                    b_time=time() #time debugging code
                    data.add_data_point(xvar,yvar,zvar,i,kelvinA) #requires virtually no extra time..
                    c_time=time() #time debugging code
                    
                            
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

#Disable all sources turn SMBs off
smbgate.set_RF_state(False) 
smb.set_RF_state(False)
HFlockin.set_output_switch0(False) 
HFlockin.set_output_switch1(False)

#record measurement time
endtime = time()
#measurementtimestring = 'Time taken: ',int((endtime-begintime)/3600),':',int(((endtime-begintime)/60)%60),':',int((endtime-begintime)%60)
print 'Time taken: ',int((endtime-begintime)/3600),':',int(((endtime-begintime)/60)%60),':',int((endtime-begintime)%60)

#reset voltage measurement
vm.set_trigger_continuous(True)
vm.set_display(1) 
if measurevoltage:
    vm2.set_trigger_continuous(True)
    vm2.set_display(1) 

data.close_file()

qt.mend()



