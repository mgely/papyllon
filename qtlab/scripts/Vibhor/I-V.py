################################
#      IMPORTS
################################

import qt
import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime

#execfile('metagen.py')

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#if 'rigol' not in instlist:
#    rigol= qt.instruments.create('rigol','rigol_dm3058',address='GPIB::7::INSTR')

if 'keithley' not in instlist:
    keithley= qt.instruments.create('keithley','Keithley_2100',address='USB0::0x05E6::0x2100::1310646::INSTR')

if 'adwin' not in instlist:
    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#measurement information stored in manual in MED instrument
med.set_device('IV on four probe device')
med.set_setup('BF')
med.set_user('Vibhor')

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()

#Set up data
filename = 'IV_data'
data = qt.Data(name=filename)
data.add_coordinate('current [uA]')
data.add_value('Voltage [mV]')
data.create_file()
data.copy_file('I-V.py')

plot1=qt.Plot2D(data, name='I vs V', coorddim=0, valdim=1)

#  VARIABLES
adwin_sweeptime=3 #sec
bias_start=-1 #V # KEEP IN MIND THE CONVERSION
bias_stop=1 #V
sweepPt=1001
V2I=100    #unit nA: this is voltage to current setting
I2V=100      #Dimensionless Voltage gain on IVVI rack
bias_list=np.linspace(bias_start,bias_stop,sweepPt)

###############################
# Measurement preparations
adwin.start_process()
while abs(adwin.get_DAC_2()-bias_start)>0.1:
    adwin.set_DAC_2(bias_start)
    qt.msleep(4)
qt.msleep(adwin_sweeptime)
#seetings for Kethley
for bias in bias_list:
    adwin.set_DAC_2(bias)
    curr_bias=bias*V2I
    qt.msleep(0.05)
    keithley.send_trigger()
    voltage=1000*keithley.read()/I2V
    data.add_data_point(curr_bias,voltage)

data.close_file()
adwin.set_DAC_2(0)
qt.mend()
#end
