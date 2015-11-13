import qt
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

begintime = time()
displayintermediatetime = True
usefinegate = True

instlist = qt.instruments.get_instrument_names()

print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if ('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgatefine',ivvi,'dac2',10*1000,0.0) #0.1x modulation
    vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
    vi.add_variable_scaled('vdd',ivvi,'dac7',1000,0.0)

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med',reset=True)

temperature = tempcon.get_kelvinA()
#measurement information
med.set_temperature(temperature)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.01 #GV/A=mV/pA
med.set_current_gain(current_gain)

#set voltages
vbias_start=-0.003 #V
vbias_stop=0.003 #V
vbias_step=0.001 #V
No_vbias = int((vbias_stop-vbias_start)/vbias_step + 1)

vgate_start=6.4 #V
vgate_stop=6.6 #V
vgate_step=0.001 #V
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
data = qt.Data(name='stability_diagram')
data.add_coordinate('Bias Voltage (V)')
data.add_coordinate('Gate Voltage (V)')
data.add_value('Current (pA)')
data.create_file()
data.copy_file('stability_diagram.py')

#actual sweep
if usefinegate:
    vgaterough = (vgate_stop+vgate_start)/2.0
    ramp(vi,'vgate',vgaterough,sweepstep,sweeptime)
    
for vg in linspace(vgate_start,vgate_stop,No_vgate):
    if usefinegate:
        ramp(vi,'vgatefine',vg-vgaterough,sweepstep,sweeptime)
    else:
        ramp(vi,'vgate',vg,sweepstep,sweeptime)
    qt.msleep(0.01)
    print 'Gate voltage: %sV' % vg
    #print 'Gate voltage offset: %sV' % (vg-vgaterough)
    
    for vb in linspace(vbias_start,vbias_stop,No_vbias):
        ramp(vi,'vbias',vb,sweepstep,sweeptime)
        qt.msleep(0.01)
        i=vm.get_readval()/current_gain*-1e3 #pA
        data.add_data_point(vb,vg,i)
                                 
        

    data.new_block()
    spyview_process(data,vbias_start,vbias_stop,vg)

    if displayintermediatetime:
        inttime = time()
        measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((inttime-begintime)/3600),"m":int(((inttime-begintime)%3600)/60),"s":int(((inttime-begintime)%3600)%60)}
        print 'Measurement time: '+ measurementtimestring
    
#generate plot, disturbs timing
plot2d = qt.Plot2D(data, name='measure2D',coorddim=0, valdim=2)
plot2d.save_png(filepath=data.get_dir()+'\\'+'plot.png')
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=2)
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')

#reset voltages
if returntozero:
    ramp(vi,'vgatefine',0,sweepstep,sweeptime)
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)

print 'Gate voltage offset: %sV' % vi.get_vgatefine()
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



