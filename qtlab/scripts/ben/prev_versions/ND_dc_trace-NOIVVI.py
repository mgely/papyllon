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

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if False|('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',lockin,'out1',1,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vgatefine',lockin,'out2',10,0.0) #0.1x modulation
    vi.add_variable_scaled('vbias',lockin,'out3',10,0.0)
    vi.add_variable_scaled('vdd',lockin,'out4',1,0.0)

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

coordinate_names = {'vgatefine':'Gate voltage offset (V)','vgate':'Gate voltage (V)','vbias':'Bias voltage (V)','Vdd':'Vdd (V)','nothing':'Nothing'}

#set x variable
xvarname = 'vbias' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc' vbias
if xvarname not in coordinate_names:
    sys.exit('Aborted: xvarname not in coordinate_names')
x_start = -0.011
x_stop =   0.011
x_step =   0.00001
if xvarname == 'nothing':
    x_stop=x_start
    Noxsteps=1
else:
    Noxsteps = round((x_stop-x_start)/x_step + 1)


#set y variable
yvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc' vbias
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = -2
y_stop = 2
y_step = 0.010
if yvarname == 'nothing':
    y_stop=y_start
    Noysteps=1
else:
    Noysteps = round((y_stop-y_start)/y_step + 1)


#set z variable
zvarname = 'nothing' # 'vgate' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc' vbias
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

#voltage ramp settings
sweepstep=.010#V
sweeptime=.005#(s) (up to max speed of ~5ms)
sweeptime2 = .005 # time to wait between set voltage and measurement


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

if (xvarname != 'Vdd') & (yvarname != 'Vdd') & (zvarname != 'Vdd'):
    Vdd_fixed = 0 # 1 V
    ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

#ready vm
vm.get_all()
if measurecontvoltage:
    vm.set_trigger_continuous(True)
else:
    vm.set_trigger_continuous(False)
vm.set_display(0)

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

#actual sweep
for zvar in linspace(z_start,z_stop,Nozsteps):

    #set z variable
    if zvarname == 'vgatefine':
        ramp(vi,'vgatefine',zvar,sweepstep,sweeptime)
    elif zvarname == 'vgate':
        vgate = zvar
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'vbias':
        ramp(vi,'vbias',zvar,sweepstep,sweeptime)
    elif zvarname == 'Vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)        

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
        elif yvarname == 'Vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)        

        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar

        counter = 0
        for xvar in linspace(x_start,x_stop,Noxsteps):

            #set x variable
            if xvarname == 'vgatefine':
                ramp(vi,'vgatefine',xvar,sweepstep,sweeptime)
            elif xvarname == 'vgate':
                vgate = xvar
                ramp(vi,'vgate',xvar,sweepstep,sweeptime)
            elif xvarname == 'vbias':
                ramp(vi,'vbias',xvar,sweepstep,sweeptime)             
            elif xvarname == 'Vdd':
                ramp(vi,'vdd',xvar,sweepstep,sweeptime)        

               
        
            
            
            qt.msleep(sweeptime2)
            if measurevoltage:
                    i=vm.get_readval() #V
            elif measurecontvoltage:
                    i=vm.get_readnextval() #requires a triger or being set in cont mode, waits until value is ready
            else:
                    i=vm.get_readval()/current_gain #pA

            kelvinA= tempcon.get_kelvinA()
            #kelvin_array=kelvinA*ones(Noxsteps)
            data.add_data_point(xvar,yvar,zvar,i,kelvinA)

            if Noxsteps > 10: #print sweep number
                if counter%int(((x_stop-x_start)/x_step+1)/10)==0:
                    print coordinate_names[xvarname] + ': %s' % xvar
                counter=counter+1

        data.new_block()
        spyview_process(data,Noxsteps,x_start,x_stop,Noysteps,y_start,y_stop,Nozsteps,z_start,zvar)    
    
#generate plot, disturbs timing
plot2d = qt.Plot2D(data, name='measure2D',coorddim=0, valdim=3)
plot2d.save_png(filepath=data.get_dir()+'\\'+'plot.png')

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



