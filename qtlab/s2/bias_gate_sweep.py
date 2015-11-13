#vi.add_variable_scaled('vgate',lockin,'out1',0.25,0.0)
#vi.add_variable_scaled('vbias',lockin,'out2',100,0.0)
#vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::16')

#PARAMTERS

v_start=-.02 #V
v_stop=20.0 #V
v_step=.001 #V

vg_start=-2
vg_stop=4.9
vg_step=.001

sweepstep=.01#V
sweeptime=.02#(s) (up to max speed of ~5ms)

#ready the lockin
#lockin.get_all()
ramp(vi,'vbias',v_start,sweepstep,sweeptime)
ramp(vi,'vgate',vg_start,sweepstep,sweeptime)
qt.msleep(1)
vi.get_vbias()
vi.get_vgate()

#ready vm
vm.set_trigger_continuous(False)
vm.get_all()

#datafile
data = qt.Data(name='33-C1_vg_sweep_1Kprobe')
data.add_coordinate('Bias Voltage [V]')
data.add_coordinate('Gate Voltage [V]')
data.add_value('Drain Current [pA]')
data.create_file()
data.copy_file('bias_gate_sweep.py')

plot2d = qt.Plot2D(data, name='measure2D', coorddim=1, valdim=2)
#spyview_process(reset=True)
for v in arange(v_start,v_stop+v_step,v_step):
    ramp(vi,'vbias',v,sweepstep,sweeptime)
    qt.msleep(0.2)
    for vg in arange(vg_start,vg_stop+vg_step,vg_step):
        ramp(vi,'vgate',vg,sweepstep,sweeptime)
        qt.msleep(0.05)
        i=vm.get_readval()
        i*=1e6
        data.add_data_point(v,vg,i)
    data.new_block()
    spyview_process(data,vg_start,vg_stop,v)
    
ramp(vi,'vbias',0,sweepstep,sweeptime)
vm.set_trigger_continuous(True)

data.close_file()

qt.mend()
