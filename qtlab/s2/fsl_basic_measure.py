#This script will take a trace over the specified freqeuncy range and resolution,
#leaving all other settings untouched.
import qt
from numpy import pi, random, arange, size
from time import time,sleep

instrument_names=qt.instruments.get_instrument_names()
if 'fsl' not in instrument_names:
    fsl=qt.instruments.create('fsl','RS_FSL',address='TCPIP::169.254.174.176::INSTR')

qt.mstart()

#CONSTANTS (Should keep these in a seperate header file or make arguments)
fstart=3000 #MHz
fstop=8000
datapoints=10000

fsl.set_start_frequency(fstart)
fsl.set_stop_frequency(fstop)
fsl.set_sweep_points(datapoints)
span=fstop-fstart

#If you want to use center and span
#center=5000.0 #MHz
#span=3000.0 #MHz
#fsl.set_center_frequency(center)
#fsl.set_span(span)

data = qt.Data(name='fsl_basic_measure')

data.add_coordinate('frequency [Hz]')
data.add_value('magnitude [dBm]')

#Need to make it so all relavent FSL setting are written to setting file!
data.create_file()

plot2d = qt.Plot2D(data, name='plot1')

#ACTUAL MEASUREMENT BEGINS

fsl.wait_to_continue() #take a trace

trace=fsl.get_trace()

for findex, a in enumerate(trace):

    fstep=span/(len(trace)-1.0)
    data.add_data_point(fstart+findex*fstep,a)



data.close_file()

qt.mend()
