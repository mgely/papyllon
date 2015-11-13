import qt
from time import time
import numpy as np

if 'keithley1' not in instlist:
    keithley1 = qt.instruments.create('keithley1','Keithley_2700',address='GPIB0::16::INSTR')

def set_dac_safe(channel,value,sweepspeed=100):

#    start = time()
    a=ivvi.get_parameters()
    #sweepspeed in mV/s of the outputvoltage!
    if a['dac%s'%channel]['multiplier'] not in [nan,0]:
        dacsweepspeed = float(sweepspeed)/a['dac%s'%channel]['multiplier']
    else:
        print "Multiplier not set"
        return False

    voltstep = float(5000)/32768   #+/-5V divided over 16 bits
    timestep = abs(voltstep/dacsweepspeed)*1000 #in ms

    ivvi.set_parameter_rate('dac%s'%channel,voltstep,timestep)
    
    ivvi.set('dac%s'%channel,value)

qt.mstart()

#Set up data

data = qt.Data(name=filename)
data.add_coordinate('Time [s]')
data.add_value('Voltage [V]')
data.create_file()

plot2d = qt.Plot2D(data, name='measure2D')

start=time()
tc=time()-start

#ivvi.set_parameter_rate('dac2',1,1)
ivvi.set('dac2',0)

while tc<0.1:
    tc=time()-start
    v=keithley1.get_readlastval()
    data.add_data_point(tc,v)

set_dac_safe(2,1000)

tc=time()-start

while tc<2:
    tc=time()-start
    v=keithley1.get_readlastval()
    data.add_data_point(tc,v)

qt.close_file()
qt.mend()
