import qt
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

begintime = time() #for measurement time calculation
returntozero = True
singletrace = True
measuretemperatureeachpoint = False

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
    ivvi.set_dac_range(3,10000) #uses altered Optodac.py

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if ('vm' not in instlist):
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if ('vm2' not in instlist):
    vm2 = qt.instruments.create('vm2','Keithley_2700',address='GPIB::16')

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
    vi.add_variable_scaled('vdd',ivvi,'dac6',1000,0.0)

if 'tempcon' not in instlist:
    tempcon = qt.instruments.create('tempcon','Lakeshore_331',address='GPIB::12')
    
#measurement information
med.set_temperature(999)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
med.set_current_gain(current_gain)

#set voltages
vbias_fixed=0.01 #V
vgate_start=5 #V
vgate_stop=8 #V
vgate_step=0.01 #V
No_vgate = int((vgate_stop-vgate_start)/vgate_step + 1)
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)
returntozero = True

#how many prints on screen per loop
if No_vgate > 10:
    NoPrints = 10
else:
    NoPrints = 2

#ready the lockin
lockin.get_all()
vi.get_vgate()
vi.get_vbias()

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)

#datafile
data = qt.Data(name='vg_sweep_vs_temperature')
data.add_coordinate('Gate Voltage (V)')
data.add_coordinate('nothing')
data.add_value('Current (pA)')
data.add_value('Temperature (K)')
data.create_file()
data.copy_file('2D_vg_sweep_vs_temperature.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#actual sweep
ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
print 'Abort measurement with Ctrl-C, data will be saved.'
i_array = zeros(No_vgate)
vg_array = linspace(vgate_start,vgate_stop,No_vgate)
value = 1
j=0
while value == 1:
    try:
        k=0
        print "Sweeps finished: %s"%j
        j_array=j*ones(No_vgate)
        T_array = tempcon.get_kelvinA()*ones(No_vgate)
        for vg in vg_array:
            ramp(vi,'vgate',vg,sweepstep,sweeptime)
            qt.msleep(0.01)
            i_array[k]=vm.get_readval()/current_gain*-1e3 #pA
            if measuretemperatureeachpoint:
                T_array[k]=tempcon.get_kelvinA()
            
            if k%int(No_vgate/(NoPrints-1))==0:
                print '=== Gate voltage: %sV ===' % vg
            k=k+1

        data.add_data_point(vg_array,j_array,i_array,T_array)
        data.new_block()
        j=j+1
        spyview_process(data,vgate_start,vgate_stop,j)
        if singletrace:
            value = 2
    except KeyboardInterrupt:
        value = 2
        break

#generate plot, disturbs timing
plot2d = qt.Plot2D(data, name='measure2D')
plot2d.save_png(filepath=data.get_dir()+'\\'+'plot.png')

#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Bias voltage: %sV' % vi.get_vbias()

#reset voltage measurement
vm.set_trigger_continuous(True)

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring

data.close_file()

qt.mend()
