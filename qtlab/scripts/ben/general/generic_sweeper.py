#
# Ben H. Schneider 2013, b.h.schneider@tudelft.nl
#
import qt
#import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime, ctime
execfile('ramp.py')

#metafile code
def spyview_process(data=0,len1=0,minval1=0,maxval1=0,len2=0,minval2=0,maxval2=0,len3=0,minval3=0,maxval3=0):
    metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w')
    metafile.write('#inner loop\n'
                   +str(len1)+'\n'
                   +str(minval1)+'\n'
                   +str(maxval1)+'\n'
                   +str(data.get_dimension_name(0))+'\n'
                   +'#outer loop\n'
                   +str(len2)+'\n'
                   +str(minval2)+'\n'
                   +str(maxval2)+'\n'
                   +str(data.get_dimension_name(1))+'\n'
                   +'#outer most loop\n'
                   +str(len3)+'\n'
                   +str(minval3)+'\n'
                   +str(maxval3)+'\n'
                   +str(data.get_dimension_name(2))+'\n'
                  )                       

    metafile.write('#values\n'
                   +'4\n'
                   +str(data.get_dimension_name(3)))
    metafile.write('#values\n'
                   +'5\n'
                   +str(data.get_dimension_name(4)))
    metafile.close()

#Install instruments
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)
if 'keithley1' not in instlist:
    keithley1 = qt.instruments.create('keithley1','Keithley_2100',address='USB0::0x05E6::0x2100::1310646::INSTR')
#if 'keithley2' not in instlist:
#    keithley2 = qt.instruments.create('keithley2','Keithley_2700',address='GPIB::17')
#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)
if 'med' not in instlist:
    med = qt.instruments.create('med','med')
if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A', address='TCPIP0::192.168.1.25::inst0::INSTR')
#if 'HFlockin' not in instlist:
#    HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)


#install instruments and its sweep multipliers, keep everything in V,A,sec,Hz,..
if False|('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('Vb',adwin,'DAC_2',1.0/(0.01*0.2),0.0) #(name,instrument, callup, scale, offset)
    vi.add_variable_scaled('Vg',adwin,'DAC_1',1.0/(4*0.2),0.0)
    #vi.add_variable_scaled('RF',smb,'RF_frequency',1e-6 ,0.0) #that's plain crazy
    #vi.add_variable_scaled('RFp',smb,'RF_power',1 ,0.0)

#Define sweepoptions
def sweep(var='none',val=0):
    if var == 'Vb':
        ramp(vi,'Vb',val,0.01,0.1) #ramp (value,sweepstep,sweeptime)
    elif var == 'Vg':
        ramp(vi,'Vg',val,0.01,0.01)
    elif var == 'none':
        sweep = 0 #do something to avoid an error
    elif var == 'RF':
        smb.set_RF_frequency(val)
    elif var == 'RFp':
        smb.set_RF_power(val)
    else:
        print 'No variable given'
    #ramp(adwin,'DAC_2',val,0.01,0.01)

#for reading values:
def measure(var='none'):
    if var == 'none':
        return 1
    elif var == 'keithley1':
        return float(eval(keithley1.a('READ?')))
    #elif var == 'keithley2':
    #    return float(eval(keithley2.a('READ?')))
    #elif var == 'Adwin':
    #    return adwin.get_ADC(31314)[0] #use adwin to read input 1 (num. averages)[dac]



mvar_1 = 'keithley1' #Use intrument to read
mmul_1 = 100e6       #multiplier for the read value
#mvar_2 = 'keithley2' #Use intrument to read
#mmul_2 = 10e6       #multiplier for the read value

#var options are 'Vb'[V],'RF'[MHz],'RFp'[dBm],'Vg'[V],'none'
#clear res sig: Vg[2.36:2.725] RF[205.86:208.02]
xvar = 'Vb'    
x_start= -0.01
x_stop = 0.01
x_resolution = 0.0001 #min: 0.02 & -13dBm 
x_pt   = 101#int(abs((x_stop-x_start)/x_resolution) +1)
x_list = np.linspace(x_start,x_stop,x_pt)
x_sleep = 0.202 #wait before taking the x-sweep 20ms is perfect for Vb

yvar = 'RFp'
y_start = -43
y_stop  = -13
y_resolution = 0.1
y_pt   = int(abs((y_stop-y_start)/y_resolution) +1)
y_list = np.linspace(y_start,y_stop,y_pt)
y_sleep = 0.3

zvar = 'none'
z_start = -1.175
z_stop  = -1.175
z_pt    = 1
z_list  = np.linspace(z_start,z_stop,z_pt)
z_sleep = 0.10

#set fixed values:
sweep('Vb',0.003) 
sweep('Vg',-1.175)
smb.set_RF_power(-13)
#smb.set_RF_frequency(200) #in MHz
smb.set_RF_state(1) #activate RF-source

print 'estimate req. time:',0.025*x_pt*y_pt*z_pt/3600, 'hours'
# Measurement preparations
med.set_device('CNT_LG04')
med.set_setup('BF')
med.set_user('Warner, Ben')
#Set up data
filename = 'LG04_21'
data = qt.Data(name=filename)
data.add_coordinate(xvar)
data.add_coordinate(yvar)
data.add_coordinate(zvar)
data.add_value('Im [A]')
data.create_file(name=filename, datadirs='D:\\data\\Ben\\CNT-Ringdown\\test')
data.copy_file('generic_sweeper.py')

adwin.start_process() #prep adwin
#adwin.set_clockcycle(30032)
adwin.set_clockcycle(300)
#prep keithley1
keithley1.ben_settings(1,2) # (Nplc ,V-range)
qt.msleep(0.5)
keithley1.send_trigger()
keithley1.set_display(0)


#generate metafile
spyview_process(data,
                len(x_list),
                x_start,
                x_stop,
                len(y_list),
                y_stop,
                y_start,
                len(z_list),
                z_start,
                z_stop)
# Sweep
qt.mstart()

#plot1=qt.Plot2D(data, name='Trace', coorddim=0, valdim=3)
z2_time = 0.0
y2_time = 0.0
x2_time = 0.0
sweep_time = 0.0
i0_time = time()
for z in z_list:
    z0_time = time()
    sweep(zvar,z)
    qt.msleep(z_sleep)

    #prepare for next loop pre sweep and wait
    sweep(yvar,y_start) 
    qt.msleep(y_sleep)
    z1_time = time()
    z2_time = z1_time - z0_time
    for y in y_list:
        y0_time = time()
        sweep(yvar,y)
        estimate_time = (x2_time*x_pt*y_pt*z_pt + y_pt*y2_time)
        print 'z: ', zvar, '[',z_start,':',z,':',z_stop,']',z_pt, 'y: ', yvar, '[',y_start,':',y,':',y_stop,']',y_pt,'x: ',xvar,'[',x_start,':',x_stop,']',x_pt
        print 'time x,y,z', x2_time ,y2_time , z2_time
        print 'Exp End :', ctime(i0_time+estimate_time)
        sweep(xvar,x_start)
        qt.msleep(x_sleep)
        y1_time = time()
        y2_time = y1_time - y0_time
        for x in x_list:
            x0_time = time()
            a = 0
            sweep(xvar,x)
            sweep_time = time() - x0_time
            meas_1 = measure(mvar_1)/mmul_1
            #meas_av = (meas_1 + measure(mvar_1)/mmul_1)/2.0
            data.add_data_point(x,
                                y,
                                z,
                                meas_1)
            x1_time = time()
            x2_time = x1_time - x0_time
i1_time = time()
print 'finished :', ctime(),' runtime :', (time()-i0_time)/3600,'hours'

# finishing
ramp_all_to_zero(vi,0.01,0.01)
keithley1.set_display(1) #turn display back on
keithley1.send_trigger()
smb.set_RF_state(0) #deactivate RF-source
data.close_file()
qt.mend()
