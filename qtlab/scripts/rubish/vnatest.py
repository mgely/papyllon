import numpy as np
import os
import qt

span=150
start_frequency=150
stop_frequency=300

qt.mstart()
data = qt.Data(name='vnameas')
data.add_coordinate('freq [MHz]')
data.add_coordinate('Gate Voltage [mV]')
data.add_value('Phase [degrees]')
data.create_file()

plot2d = qt.Plot2D(data, name='measure2D')
plot3D = qt.Plot3D(data, name='measure3D')

for vg in np.arange(0,5000,100):
    ivvi.set('dac2',vg)
    qt.msleep(0.1)
    trace=vna.get_trace()
    fstep=span/(len(trace)-1.0)
    flist=np.arange(start_frequency,stop_frequency+fstep,fstep)
    output=[flist,trace]
    data.add_data_point(output[0],[vg]*len(output[0]),output[1])
    data.new_block()

data.close_file()
qt.mend()

