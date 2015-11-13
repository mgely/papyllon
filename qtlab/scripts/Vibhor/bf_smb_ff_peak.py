import qt
import numpy
import visa
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')

if 'ff' not in instlist:
    ff=visa.instrument('TCPIP0::192.168.1.151::inst0::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#measurement information stored in manual in MED instrument
med.set_device('sideband_out')
med.set_setup('BF and neat drum')
med.set_user('Vibhor')

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()

#Set up data
filename = 'IV_data'
data = qt.Data(name=filename)
data.add_coordinate('smb drive [dBm]')
data.add_value('power out [dBm]')
#data.create_file()
data.create_file(name=filename, datadirs='D:\\data\\Vibhor\\neatDrum\\20140101\\')
data.copy_file('bf_smb_ff_peak.py')
plot1=qt.Plot2D(data, name='smb drive vs power out', coorddim=0, valdim=1)

#  VARIABLES
power_start=-20
power_stop=30
sweepPt=26
power_list=np.linspace(power_start,power_stop,sweepPt)
###############################
# Measurement preparations

#seetings for smb
for pw in power_list:
    smb2.set_RF_power(pw)
    qt.msleep(2)
    ff.write('CALC:MARK1:FUNC:MAX')
    qt.msleep(0.5)
    pw_out=eval(ff.ask('CALC:MARK1:Y?'))
    data.add_data_point(pw,pw_out)

data.close_file()
qt.mend()
#end
