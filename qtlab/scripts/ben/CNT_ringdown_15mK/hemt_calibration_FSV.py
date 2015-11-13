#
# Ben H. Schneider 2013, b.h.schneider@tudelft.nl
#
import qt
#import numpy
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime, ctime
import visa
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
    metafile.write('#values\n'
                   +'6\n'
                   +str(data.get_dimension_name(5)))
    metafile.write('#values\n'
                   +'7\n'
                   +str(data.get_dimension_name(6)))
    metafile.write('#values\n'
                   +'8\n'
                   +str(data.get_dimension_name(7)))
    metafile.close()

#Install instruments
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)
if 'keithley1' not in instlist:
    keithley1 = qt.instruments.create('keithley1','Keithley_2100',address='USB0::0x05E6::0x2100::1310646::INSTR')
if 'med' not in instlist:
    med = qt.instruments.create('med','med')
#if 'ff' not in instlist:
#    ff=visa.instrument('TCPIP0::A-N9916A-01189::inst0::INSTR')
if 'HFlockin' not in instlist:
    HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)
if 'smb1' not in instlist:
    smb1 = qt.instruments.create('smb1','RS_SMB100A', address='TCPIP0::192.168.1.102::inst0::INSTR')
if 'smb2' not in instlist:
    smb2 = qt.instruments.create('smb2','RS_SMB100A', address='TCPIP0::192.168.1.25::inst0::INSTR')
#if 'smb3' not in instlist:
#    smb3 = qt.instruments.create('smb3','RS_SMB100A', address='TCPIP0::192.168.1.50::inst0::INSTR')
#if 'adwin' not in instlist:
#    adwin= qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)
if 'fsv' not in instlist:
    fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136')
#if 'pna' not in instlist:
#    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')


#install instruments and its sweep multipliers, keep everything in V,A,sec,Hz,..
if False|('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    HFlockin.set_auxmode(0,-1)  #sets aux 1 to manual
    HFlockin.set_auxmode(1,-1)  #sets aux 2 to manual
    HFlockin.set_auxmode(2,-1)  #sets aux 3 to manual
    #HFlockin.set_auxmode(3,-1)  #sets aux 4 to manual
    vi.add_variable_scaled('Vb',HFlockin,'auxoffset1',1.0/(0.01*0.2),0.0)
    vi.add_variable_scaled('Vg',HFlockin,'auxoffset0',1.0/(4*0.2),0.0) #with the 10 to 1 vdivider 9.253*100 10mV/1V 1V/10V -> 10mV/10V
    vi.add_variable_scaled('Vs',HFlockin,'auxoffset2',1.0/(0.2),0.0)
    #vi.add_variable_scaled('Vb',adwin,'DAC_2',1.0/(0.01*0.2),0.0) #(name,instrument, callup, scale, offset)
    #vi.add_variable_scaled('Vg',adwin,'DAC_1',1.0/(4*0.2),0.0)
    #vi.add_variable_scaled('Vdd',adwin,'DAC_2',1.0/(0.2),0.0)

#Define sweepoptions
def sweep(var='none',val=0,delta=0):
    if var == 'Vb':
        ramp(vi,'Vb',val,0.01,0.1) #ramp (value,sweepstep,sweeptime)
    elif var == 'Vg':
        ramp(vi,'Vg',val,0.01,0.01)
    elif var == 'none':
        sweep = 0 #do something to avoid an error
    elif var == 'RF1':
        smb1.set_RF_frequency(val)
    elif var == 'RFp1':
        smb1.set_RF_power(val)
    elif var == 'RF2':
        smb2.set_RF_frequency(val)
    elif var == 'RFp2':
        smb2.set_RF_power(val)
    elif var == 'RF3':
        smb3.set_RF_frequency(val)
    elif var == 'RFp3':
        smb3.set_RF_power(val)
    elif var == 'Vs':
        ramp(vi,'Vs',val,0.01,0.01)
    elif var == '2smbs':
        #print '2smbs sweepvariable needs to be activated first'
        smb1.set_RF_frequency(val)
        smb2.set_RF_frequency(val-delta)
    elif var == 'Tc':
        HFlockin.set_timeconstant0(10**val)
    elif var == 'FF_pow':
        ff.write('SOUR:POW '+str(val))
    elif var == 'Frequency [MHz]':
        print ' '
#    elif var == 'PNAp':
#        pna.set_power(val)
    else:
        print 'Invalid sweep option'
    #ramp(adwin,'DAC_2',val,0.01,0.01)

#for reading values: output is an array
def measure(v0_list=[],v0_name='none',v2_name='none',v2_mul=1,delta =0):
    '''
    The idea is to get all values in Array or list form,
    so it can be used for PNAs, as well as a Keithleys..
    v0_list is the list to be sweeped
    v0_name defines what this is i.e. Vg, Vb, RF, RFp, PNA_RF,PNA_POW,...
    v2_name selects the measurement unit: keithley1, Adwin, PNA, ...
    v2_mul is used to scale i.e. dac multipliers... (measured data will be deviced by v2_mul)
        example: measure(x_list,xvar,mvar_1,mmul_1)...
    '''
    if v2_name == 'none':
        return 1
    elif v2_name == 'keithley1':
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0)
            read_0 = float(eval(keithley1.a('READ?')))
            meas_1 = read_0/v2_mul
            i_array[i] = meas_1
            i = i+1
        return i_array
    elif v2_name == 'Adwin':
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0)
            read_0 = adwin.get_ADC(31314)[0] #(averages)[dac]
            meas_1 = read_0/v2_mul
            i_array[i] = meas_1
            i = i+1
        return i_array
    elif v2_name == 'FSV':
        fsv.set_start_frequency(v0_list[0])
        fsv.set_stop_frequency(v0_list[-1])
        fsv.set_sweeppoints(len(v0_list))
        fsv.write('INIT;*WAI')
        trace= fsv.get_trace()
        return trace
    
    elif v2_name == 'HFLockin':
        ''' Only record with Lockin'''
        timec = HFlockin.get_timeconstant0() #used for sleep before measuring

        i_array0 = zeros(len(v0_list)) #[0,0..]
        i_array1 = zeros(len(v0_list)) #[0,0..]
        i_array2 = zeros(len(v0_list)) #[0,0..]
        i_array3 = zeros(len(v0_list)) #[0,0..]
        i_array4 = zeros(len(v0_list)) #[0,0..]

        i = 0
        v0 = 0 #the variable to be sweeped
        for v0 in v0_list:
            sweep(v0_name,v0,delta) #set SMB frequencies with difference freq delta.
            i_array0[i] = HFlockin.get_x()
            i_array1[i] = HFlockin.get_y()
            i_array2[i] = HFlockin.get_amplitude()
            i_array3[i] = HFlockin.get_phase()
            i = i+1

        return i_array0,i_array1,i_array2,i_array3

    elif v2_name == 'HFL_Keith':
        '''record with HF-Lockin and Keithley'''
        timec = HFlockin.get_timeconstant0()
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array0 = zeros(len(v0_list)) #[0,0..]
        i_array1 = zeros(len(v0_list)) #[0,0..]
        i_array2 = zeros(len(v0_list)) #[0,0..]
        i_array3 = zeros(len(v0_list)) #[0,0..]
        i_array4 = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0,delta) #set SMB frequencies with difference freq delta.

            i_array4[i] = float(eval(keithley1.a('READ?')))/v2_mul #record DC
            qt.msleep(timec)

            i_array3[i] = HFlockin.get_phase()
            i_array0[i] = HFlockin.get_x()
            i_array1[i] = HFlockin.get_y()
            i_array2[i] = HFlockin.get_amplitude()

            i = i+1

        return i_array0,i_array1,i_array2,i_array3,i_array4

    elif v2_name == 'PNA':
        pna.sweep()
        return pna.fetch_data(polar=True)

    elif v2_name == 'PNA_single':
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array0 = zeros(len(v0_list)) #[0,0..]
        i_array1 = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0)
            read_0 = array(measure([0],'none','PNA',1))
            meas = read_0/v2_mul
            i_array0[i] = meas[0]
            i_array1[i] = meas[1]
            i = i+1
        return i_array0,i_array1

    elif v2_name == 'FieldFox':
        f_start=v0_list[0]*1e6 #in Hz
        f_stop=v0_list[-1]*1e6 #in Hz
        ff.write('FREQ:START '+str(f_start))
        qt.msleep(0.005)
        ff.write('FREQ:STOP '+str(f_stop))
        qt.msleep(0.005)
        ff.write('SWE:POIN '+str(len(v0_list)))
        qt.msleep(0.005)
        ff.write('INIT;*OPC') #initiate sweep
        #wait till sweep is finished
        a = 0
        x = 0
        y = 0
        while a==0:
            qt.msleep(0.05)
            try:
                a=eval(ff.ask('*OPC?'))
                break
            except(KeyboardInterrupt, SystemExit):
                raise
            except:
                a=0
        trace = eval(ff.ask('CALCulate:DATA:SDATA?'))
        x = array(trace[::2])/v2_mul
        y = array(trace[1::2])/v2_mul
        r = sqrt(abs(x**2+y**2))

        i = 0
        nn = 0
        x2 = x
        for i in x2:
            if i == 0:
                x2[nn]=x2[nn-1] #find and change zeros from x2_array
            nn+=1
        t = arctan(y/x2) #in radians
        
        return x,y,r,t

###############################################################
filename = 'dev'

mvar_1 = 'FSV'  #Use intrument to read (keithley1,PNA_single,Adwin,FSV), HFLockin_2smbs
mmul_1 = 1       #multiplier for the read value
delta = 313 #7.197 #MHz

#var options are 'Vb'[V],'RF1 [MHz],RFp1 [dBm],'Vg'[V],'none','Tc' (time constant [10**x])
#clear res sig: Vg[2.36:2.725] RF[205.86:208.02]
#LO (vg_Pow min is about 7dBm)

xvar = 'Frequency [MHz]'    
x_start= delta -0.002
x_stop = delta +0.002
x_resolution = 0.1 #min: 0.02 & -13dBm 
x_pt   = 1001#int(abs((x_stop-x_start)/x_resolution) +1)
x_list = np.linspace(x_start,x_stop,x_pt)
x_sleep = 1.0 #wait before taking the x-sweep 20ms is perfect for Vb

yvar = '2smbs'
y_start = 600
y_stop  = 800
y_resolution = 20
y_pt   = int(abs((y_stop-y_start)/y_resolution) +1)
y_list = np.linspace(y_start,y_stop,y_pt)
y_sleep = 0

zvar = 'RFp1'
z_start = 10
z_stop  = 0
z_resolution = 1
z_pt    = int(abs((z_stop-z_start)/z_resolution) +1)
z_list  = np.linspace(z_start,z_stop,z_pt)
z_sleep = 0

#SMB2 is connected to Vg AC in
smb2.set_RF_power(-30)
smb2.set_RF_state(1)
smb2.set_RF_frequency(468)

#SMB1 is connected to Hemt
smb1.set_RF_power(0)
smb1.set_RF_state(1)
smb1.set_RF_frequency(768)

sweep('Vs', 0.3) #activate Hemt

#set fixed values:
#sweep('Vb',0.003)
#sweep('Vg',2.56278)
#smb_vg.set_RF_power(7) #7dBm is optimum see calibration folder.
#smb_vg.set_RF_frequency(200) #in MHz
#smb_vg.set_RF_state(1) #activate RF-source

#Hemt activation
#smb_hemt.set_RF_power(14)
#smb_hemt.set_RF_frequency(190) #in MHz

#smb_hemt.set_RF_state(1) #activate RF-source
# when using '2smbs'

#set difference frequency here:

#HFLockin prep:
HFlockin.set_impedance50Ohm0(True)
HFlockin.set_reference('Signal Input 2')
sweep('Tc',-3.5) #

################################################################
print 'estimate req. time:',0.027*x_pt*y_pt*z_pt/3600, 'hours'
# Measurement preparations
med.set_device('CNT_LG04')
med.set_setup('BF')
med.set_user('Warner, Ben')
#Set up data
data = qt.Data(name=filename)
data.add_coordinate(xvar)
data.add_coordinate(yvar)
data.add_coordinate(zvar)
data.add_value('FSV [dBm]')
#data.add_value('Lockin X')
#data.add_value('Lockin Y')
#data.add_value('Lockin R')
#data.add_value('Lockin Theta')
#data.add_value('DC')
#data.add_value('FFox [X]')
#data.add_value('FFox [Y]')
#data.add_value('FFox [abs]')
#data.add_value('FFox [phase]')
data.create_file(name=filename, datadirs='D:\\data\\Ben\\CNT-Ringdown\\Hemt_calibration')
data.copy_file('generic_sweeper.py')

#adwin.start_process() #prep adwin
#adwin.set_clockcycle(30032)
#adwin.set_clockcycle(300)
#prep keithley1
keithley1.ben_settings(1,2) # (Nplc ,V-range)
qt.msleep(0.5)
keithley1.send_trigger()
keithley1.set_display(1)
#prepare fsv
#fsv.set_trace_continuous(False)
#fsv_time=fsv.get_sweeptime()*fsv.get_averages()


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
nn = 0
#plot1=qt.Plot2D(data, name='Trace', coorddim=0, valdim=3)
z2_time = 0.0
y2_time = 0.0
x2_time = 0.0
sweep_time = 0.0
i0_time = time()
for z in z_list:
    z0_time = time()
    sweep(zvar,z,delta)
    qt.msleep(z_sleep)

    #prepare for next loop pre sweep and wait
    sweep(yvar,y_start,delta) 
    qt.msleep(y_sleep)
    z1_time = time()
    z2_time = z1_time - z0_time
    for y in y_list:
        nn +=1
        y0_time = time()
        sweep(yvar,y,delta)
        #estimate_time = (x2_time*y_pt*z_pt + y_pt*y2_time +z_pt*z2_time)
        estimate_time = ((time()-i0_time)/nn)*y_pt*z_pt
        print 'z: ', zvar, '[',z_start,':',z,':',z_stop,']',z_pt, 'y: ', yvar, '[',y_start,':',y,':',y_stop,']',y_pt,'x: ',xvar,'[',x_start,':',x_stop,']',x_pt
        print 'time x,y,z', x2_time ,y2_time , z2_time
        print 'Exp End :', ctime(i0_time+estimate_time)
        sweep(xvar,x_start,delta)
        qt.msleep(x_sleep)
        y1_time = time()
        y2_time = y1_time - y0_time

        x0_time = time()

        #get all arrays here:
        x_array = x_list
        y_array = y*ones(x_pt)
        z_array = z*ones(x_pt)
        i_array = measure(x_list,xvar,mvar_1,mmul_1,delta) #sweeps xvar and creates an array (see top)

        x1_time = time()
        x2_time = x1_time - x0_time
        
        
        #Store data into Dat file
        '''
        data.add_data_point(x_array,
                            y_array,
                            z_array,
                            i_array[0],
                            i_array[1],
                            i_array[2],
                            i_array[3])#,
                            #i_array[4])
        '''
        data.add_data_point(x_array,
                            y_array,
                            z_array,
                            i_array)
        

i1_time = time()
print 'finished :', ctime(),' runtime :', (time()-i0_time)/3600,'hours'


# finishing
ramp_all_to_zero(vi,0.01,0.01)
keithley1.set_display(1)
keithley1.send_trigger()
#smb_hemt.set_RF_state(0)
#smb_vg.set_RF_state(0)
data.close_file()
qt.mend()
