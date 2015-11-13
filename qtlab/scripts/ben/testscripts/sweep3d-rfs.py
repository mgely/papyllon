#prepare environment
import qt
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
execfile('metagen3D_ben.py')
filename = 'pow_set2'

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

#activate if needed
#fsv = qt.instruments.create('fsv','RS_FSV', address='GPIB::20::INSTR')
#fsv = qt.instruments.create('fsv','RS_FSV', address='TCPIP0::192.168.1.136::inst0::INSTR')
#lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')
#smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')
#smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')

#HFlockin.set_output_switch0(True)
smbgate.set_RF_state(True)
smb.set_RF_state(True)

qt.mstart()

data = qt.Data(name=filename)
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Lockin [V]')
data.add_coordinate('Power [dBm]')
data.add_value('Output [dBm]')
data.create_file()
data.copy_file('sweep3d.py')


####Settings:
kHz = 1e3
MHz = 1e6
GHz = 1e9

#dim 1
f1_start= fsv.get_start_frequency()  #*MHz #whatever is set on the display (val. in MHz)
f1_stop= fsv.get_stop_frequency()  #*MHz
f1_pts = fsv.get_sweeppoints()
#dim 2
lpow_start = 0.001 #in log space 0 is not allowed!
lpow_stop = 1
lpow_pts = 21
#dim 3
#power in dBm first, adding a V option later
pow_start= 0
pow_stop= -40
pow_pts = 41

#dim1
#prepare fsv
fsv.set_trace_continuous(False)
fsv_time=fsv.get_sweeptime()*fsv.get_averages()
#dim2
#prepare lockin
lockin_range = 1 #range to pm 1V
HFlockin.set_output_range0(lockin_range) #sets the range setting to 1 V
HFlockin.set_power000(lpow_start,lockin_range)
#dim3
#prepare smb
smbgate.set_RF_power(pow_start)


# making lists of values for the sweep
f_list=np.linspace(float(f1_start),float(f1_stop),(f1_pts))
lpow_list=np.linspace(float(lpow_start),float(lpow_stop),(lpow_pts))
pow_list=np.linspace(float(pow_start),float(pow_stop),(pow_pts))

#in logspace
#lpow_list=np.logspace(log10(float(lpow_start)),log10(float(lpow_stop)),(lpow_pts))


#create a metafile upfront (not good to put it in a loop with pow_stop varying) allows watching the data while aquiring it
spyview_process(data,len(f_list),f1_start,f1_stop, len(lpow_list),lpow_stop,lpow_start, len(pow_list),pow_start,pow_stop)

print 'measurement loop:'
#do the actual sweep
j= 0 #counter to see how far the measurement went
for f1_power in pow_list:
    #dim3
    j+=1
    power_list= list(f1_power*ones(len(f_list))) #make a list of the same length as the array to be placed into the data file
    smbgate.set_RF_power(f1_power)
    print 'RF_power =', f1_power, 'dBm'
    for l1_power in lpow_list :
        #dim2
        HFlockin.set_power000(l1_power,lockin_range) #set lockin voltage
        lpower_list= list(l1_power*ones(len(f_list))) #make a list of the same length as the array to be placed into the data file
        print 'Lockin Voltage =', l1_power, 'V'
        #dim1
        fsv.write('INIT;*WAI')
        trace_list= fsv.get_trace()
        #qt.msleep(fsv_time) #in combination with cont. sweep
        '''
        now we have:
        f_list (freq point) X
        lpower_list (Lockin Voltage) Y
        Power_list (RF power) Z
        trace_list (Measured dBms) Values
        '''
        data.add_data_point(f_list,lpower_list,power_list,trace_list) #store data(lists) to file
        data.new_block() #add an empty line
        

#sweep finished close file and turn off systems
data.close_file()
qt.mend()
smbgate.set_RF_state(False)
HFlockin.set_output_switch0(False)
