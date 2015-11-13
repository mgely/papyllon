################################
#       DESCRIPTION
################################

#Set of functions and commands that setup up the intruments and variables such \
# that the biasing functions can operate.


################################
#       DEVELOPMENT NOTES/LOG
################################



################################
#      IMPORTS
################################

import qt
import numpy as np
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
import pylab
#execfile('metagen2D.py')
execfile('metagen3D.py')
execfile('support_functions.py')

################################
#      VARIABLES
################################

base_path = 'D:\\data\\Sal\\EOS8C\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

filename = 'biasing'
path = base_path+date_path+'_____'+filename

start_cav = 5.31e9
stop_cav = 5.33e9
f_points_cav = 51
ifbw_cav = 100
pow_cav  = 10
aver_cav = 1

f_cw = 5.3218e9

fcav_list=np.linspace(float(start_cav),float(stop_cav),f_points_cav)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A_sal', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#############################################
#      INSTRUMENTS INITIALISATION
#############################################

pna.reset()

#setup two displays
pna.w("DISP:WIND1:STATE ON")
pna.w("DISP:WIND2:STATE ON")

pna.w("INIT:CONT OFF")          #switch to manual triggering, it triggers all channels globally

#setup cavity scan (magnitude)
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.w("DISP:WIND1:TRACE1:FEED 'CH1_S21_S1'")
pna.w("CALC1:PAR:SEL 'CH1_S21_S1'")
pna.w("CALC1:FORM MLOG")

pna.w("SENS:FREQ:START %s" % (start_cav))
pna.w("SENS:FREQ:STOP %s" % (stop_cav))
pna.w("SENS:SWE:POIN %s" % (f_points_cav))
pna.w("SENS:BWID %s" % (ifbw_cav))
pna.w("SENS:AVER 1")
pna.w("SENS:AVER:MODE POIN")
pna.w("SENS:AVER:COUN %s" % (aver_cav))

#do peak detection
pna.w("CALC1:MARK ON")
pna.w("CALC1:MARK:FUNC MAX")
pna.w("CALC1:MARK:FUNC:TRAC ON")

#### set triggering per channel
pna.w("SENS1:SWE:MODE HOLD")
pna.w("SENS1:SWE:MODE HOLD")
pna.w("TRIG:SCOP CURR")
