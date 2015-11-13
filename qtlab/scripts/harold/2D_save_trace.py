import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen.py')

begintime = time() #for measurement time calculation
recorddc=False #also record dc current?

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if True:#'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',lockin,'out1',1,0.0)
    vi.add_variable_scaled('vdd',lockin,'out3',1,0.0)

if 'med' not in instlist:
    med = qt.instruments.create('med','med',reset=True)

if True:#'vna' not in instlist:
    vna = qt.instruments.create('vna','RS_ZVB',address='GPIB::21')
    
#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')

#set frequencies
x_start=0.009 #MHz
x_stop=4000 #MHz

#set y variable
coordinate_names = {'Vdd':'Vdd (V)','vgate':'Gate voltage (V)'}
yvarname = 'Vdd' # 'vgate' or 'Vdd'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 0
y_stop = 1.5
y_step = 0.1

#set fixed values
#vbias_fixed=0.001 #V
if yvarname != 'vgate':
    vgate_fixed = 0 #V
    ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vgate_fixed

if yvarname != 'Vdd':
    Vdd_fixed = 0 #V
    ramp(vi,'vgate',Vdd_fixed,sweepstep,sweeptime)
    print '+++ Vdd: %sV +++' % Vdd_fixed

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)
returntozero = True

filename='lg-04xx31b2_2D_VNA_trace_vs_'+yvarname

qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the vna
vna.set_source_power(-20) #dBm
vna.set_resolution_bandwidth(0.001) #MHz
x_sweeppoints=201
vna.set_sweeppoints(x_sweeppoints)
x_step=(x_stop-x_start)/(x_sweeppoints-1)
x_array = arange(x_start,x_stop+x_step,x_step)
vna.set_RF_state(True)

#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_value('S21 (dB)')
data.create_file()
data.copy_file('2D_save_trace.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep

for yvar in arange(y_start,y_stop+y_step,y_step):
    #set y variable
    if yvarname == 'vgate':
        ramp(vi,'vgate',yvar,sweepstep,sweeptime)
    elif yvarname == 'Vdd':
        ramp(vi,'vdd',yvar,sweepstep,sweeptime)
        
    qt.msleep(1)
    print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar
    V_array = vna.get_trace()
    y_array = yvar*ones(x_sweeppoints)
    

    data.add_data_point(x_array,y_array,V_array)

    data.new_block()
    spyview_process(data,x_start,x_stop,yvar)

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=2)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=2)

plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')

#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vdd',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Vdd: %sV' % vi.get_vdd()

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}
print 'Measurement time: '+ measurementtimestring

vna.set_RF_state(False)

data.close_file()

qt.mend()
