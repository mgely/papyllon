import qt
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',lockin,'out1',1,0.0)
    vi.add_variable_scaled('vbias',lockin,'out2',100,0.0)

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
med.set_current_gain(current_gain)

#set voltages
vbias_fixed=0.01 #V
vgate_start=5 #V
vgate_stop=8.5 #V
vgate_step=0.005 #V
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
data = qt.Data(name='vg_sweep')
data.add_coordinate('Gate Voltage (V)')
data.add_value('Current (pA)')
data.create_file()
data.copy_file('vg_sweep.py')

#actual sweep
ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
for vg in arange(vgate_start,vgate_stop+vgate_step,vgate_step):
    ramp(vi,'vgate',vg,sweepstep,sweeptime)
    qt.msleep(0.01)
    i=vm.get_readval()/current_gain*-1e3 #pA
    data.add_data_point(vg,i)

#generate plot, disturbs timing
plot2d = qt.Plot2D(data, name='measure2D')
plot2d.save_png(filepath=data.get_dir()+'\\'+'plot.png')

#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)

#reset voltage measurement
vm.set_trigger_continuous(True)

data.close_file()

qt.mend()
