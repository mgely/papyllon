
import numpy as np
import os
import qt

execfile('metagen1D.py')

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'fsl' not in instlist:
    fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')

qt.mstart()
data = qt.Data(name='grab_spectrum')
data.add_coordinate('Frequency [MHz]')
data.add_value('Magnitude [dBm]')
data.create_file()
data.copy_file('grab_spectrum.py')

#initialize spyview meta.txt file
spyview_process(reset=True)



fsl.get_all()

#fsl.set_trace_continuous(False)#mstart should do this, but...

trace=fsl.grab_trace() #actual measurement

    
#convert trace (list of amplitudes) to data, (frequency, amplitude) pairs:
span=fsl.get_span()
start_frequency=fsl.get_start_frequency()
stop_frequency=fsl.get_stop_frequency()
fstep=span/(len(trace)-1.0)

flist=linspace(start_frequency,stop_frequency,len(trace))
out=[flist,trace]

#fsl.set_trace_continuous(True)#mend should do this, but...

data.add_data_point(out[0],out[1])

spyview_process(data,start_frequency,stop_frequency)

plot2d = qt.Plot2D(data, name='measure2D')
plot2d.save_png(filepath=data.get_dir()+'\\'+'plot2d.png')

data.close_file()
qt.mend()

      
        

    
