import qt
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

begintime = time()
usefinegate = False
returntozero =True

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
    ivvi.set_dac_range(3,10000) #uses altered Optodac.py

if False|('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgatefine',ivvi,'dac2',10*1000,0.0) #0.1x modulation
    vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
    vi.add_variable_scaled('vdd',ivvi,'dac7',1000,0.0)

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med',reset=True)

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
med.set_current_gain(current_gain)

#set voltages
vbias_start=-0.010 #V
vbias_stop=0.010 #V
vbias_step=0.010 #V
No_vbias = int((vbias_stop-vbias_start)/vbias_step + 1)

vgate_start=-8.5 #V
vgate_stop=8.5 #V
vgate_step=0.1 #V
No_vgate = int((vgate_stop-vgate_start)/vgate_step + 1)

sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)
returntozero = True

#ready the lockin
lockin.get_all()
vi.get_vgate()
vi.get_vbias()

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)

#datafile
data = qt.Data(name='bias_gate_sweep')
data.add_coordinate('Bias Voltage (V)')
data.add_coordinate('Gate Voltage (V)')
data.add_value('Current (pA)')
data.create_file()
data.copy_file('bias_gate_sweep.py')

if usefinegate:
    vgaterough = (vgate_stop+vgate_start)/2.0
    ramp(vi,'vgate',vgaterough,sweepstep,sweeptime)

#actual sweep
for vb in linspace(vbias_start,vbias_stop,No_vbias):
    ramp(vi,'vbias',vb,sweepstep,sweeptime)
    #qt.msleep(0.01)
    print '=== Bias voltage: %sV ===' % vb
    counter = 0
    for vg in linspace(vgate_start,vgate_stop,No_vgate):
        if usefinegate:
            ramp(vi,'vgatefine',vg-vgaterough,sweepstep,sweeptime)
        else:
            ramp(vi,'vgate',vg,sweepstep,sweeptime)
        
        qt.msleep(0.01)
        i=vm.get_readval()/current_gain*-1e3 #pA
        data.add_data_point(vb,vg,i)

        if No_vgate > 20:
            if counter%int(((vgate_stop-vgate_start)/vgate_step+1)/20)==0:
                print 'Gate voltage: %sV' % vg
            counter=counter+1

    data.new_block()
    spyview_process(data,vgate_start,vgate_stop,vb)
    
#generate plot, disturbs timing
plot2d = qt.Plot2D(data, name='measure2D',coorddim=1, valdim=2)
plot2d.save_png(filepath=data.get_dir()+'\\'+'plot.png')

#reset voltages
if returntozero:
    ramp(vi,'vgatefine',0,sweepstep,sweeptime)
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Bias voltage: %sV' % vi.get_vbias()

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int(1/3600*(endtime-begintime)),"m":int(1/60*(endtime-begintime)),"s":int(1*(endtime-begintime))}
print 'Measurement time: '+ measurementtimestring

#reset voltage measurement
vm.set_trigger_continuous(True)

data.close_file()

qt.mend()



