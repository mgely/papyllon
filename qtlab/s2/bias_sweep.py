#vi.add_variable_scaled('vout',lockin,'out1',0.25,0.0)

v_start=-.01 #V
v_stop=.01 #V
v_step=.001 #V

sweepstep=.001#V
sweeptime=.01#(s) (up to max speed of ~5ms)

#ready the lockin
lockin.get_all()
vi.get_vout()
ramp(vi,'vbias',v_start,sweepstep,sweeptime)
qt.msleep(1)

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)

#datafile
data = qt.Data(name='vg_sweep')
data.add_coordinate('Bias Voltage [V]')
data.add_value('Current [pA]')
data.create_file()

plot2d = qt.Plot2D(data, name='measure2D')

for vg in arange(v_start,v_stop+v_step,v_step):
    ramp(vi,'vbias',vg,sweepstep,sweeptime)
    qt.msleep(0.2)
    i=vm.get_readval()
    i*=1e6
    data.add_data_point(vg,i)

ramp(vi,'vbias',0,sweepstep,sweeptime)
vm.set_trigger_continuous(True)

data.close_file()

qt.mend()
