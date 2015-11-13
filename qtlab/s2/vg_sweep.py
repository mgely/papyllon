v_start=0 #V
v_stop=1 #V
v_step=.1 #V
sweepstep=.001#V
sweeptime=.01#(s) (up to max speed of ~5ms)

#ready the lockin
lockin.get_all()
vi.get_vout()

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)

#datafile
data = qt.Data(name='vg_sweep')
data.add_coordinate('Gate Voltage [V]')
data.add_value('Current [UNITS]')
data.create_file()

plot2d = qt.Plot2D(data, name='measure2D')

for vg in arange(v_start,v_stop,v_step):
    ramp(vi,'vout',vg,sweepstep,sweeptime)
    qt.msleep(0.1)
    i=vm.get_readval()
    data.add_data_point(vg,i)

vm.set_trigger_continuous(True)

data.close_file()

qt.mend()
