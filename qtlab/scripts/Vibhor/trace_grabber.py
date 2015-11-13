#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
   

filename = 'trace_grabber'
data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_value('spectrum')
#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\post-Trieste\\20131007\\')
data.copy_file('trace_grabber.py')

####Settings (JUST FOR LOGGING)
#Current temperature
# Gate = 3.12
#610 mK
# SMB2 frq = 5930.110MHz
# SMB2 at 16 dBm +0dB CPL +ISOlator + split (6 dB) + to the device -37
# Same source used for carrier cancellation
#HEMT+BLUE CABLE+ 0 (10dB CPL used for carrier cancel)+miteq+miteq 
numpt=fsv.get_sweeppoints()
st=fsv.get_start_frequency()
sp=fsv.get_stop_frequency()
freq=np.linspace(st,sp,numpt)
trace= fsv.get_trace2()
data.add_data_point(freq,trace)
data.new_block()
qt.msleep(0.01)
data.close_file()

qt.mend()




