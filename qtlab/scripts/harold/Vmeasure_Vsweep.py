import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen1D.py')

begintime = time() #for measurement time calculation

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vdd',lockin,'out3',1,0.0)

if 'vm' not in instlist:
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')

#set voltages
x_start=0 #V
x_stop=1 #V
x_step=0.01 #V

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)
returntozero = True



filename='31b2_Vd_vs_Vdd'

qt.mstart()

#ready vm
vm.get_all()
vm.set_trigger_continuous(False)

#ready the lockin
lockin.get_all()

#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('V_dd (V)')
data.add_value('V_s (V)')
data.create_file()
data.copy_file('Vmeasure_Vsweep.py')
data.copy_file('ramp.py')
data.copy_file('metagen1D.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep

counter = 0
for x_var in arange(x_start,x_stop+x_step,x_step):
    ramp(vi,'vdd',x_var,sweepstep,sweeptime)
    qt.msleep(.05)
    V = vm.get_readval() #value
    data.add_data_point(x_var,V)
    
   
    if counter%int(((x_stop+x_step-x_start)/x_step+1)/(10-1))==0:
        print 'Vdd: %sV' % x_var
    counter=counter+1


spyview_process(data,x_start,x_stop,0)


plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=1)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')

#reset voltages
if returntozero:
    ramp(vi,'vdd',0,sweepstep,sweeptime)
    

print 'Vdd: %sV' % vi.get_vdd()

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}
print 'Measurement time: '+ measurementtimestring

vm.set_trigger_continuous(True)

data.close_file()

qt.mend()
