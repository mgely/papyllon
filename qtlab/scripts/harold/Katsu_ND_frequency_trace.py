import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen3D.py')

begintime = time() #for measurement time calculation
inttime = time()

returntozero = True #sweep voltages back to zero?
displayintermediatetime=True

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if True or ('fsl' not in instlist):
    fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')
    
if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if ('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vug',lockin,'out1',1,0.0) 
    vi.add_variable_scaled('vlg',lockin,'out2',1,0.0)
    vi.add_variable_scaled('vbg',lockin,'out3',1,0.0)

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

#carrier
if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

#signal
if 'smb' not in instlist:
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::30::INSTR')

#measurement information
temperature = 300
med.set_temperature(temperature)
med.set_device('Katsus device?')
med.set_setup('Katsus setup?')
med.set_user('Katsu')

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

#set frequencies
RF_start_fixed=200 #MHz
RF_stop_fixed=750 #MHz
RF_step=0.5#MHz

NoRFsteps = int((RF_stop_fixed-RF_start_fixed)/RF_step + 1)
RF_center = (RF_start_fixed+RF_stop_fixed)/2.0
RF_array_fixed = linspace(RF_start_fixed,RF_stop_fixed,NoRFsteps)

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2
    
#coordinates that can be changed, including nothing
coordinate_names = {'vug':'UG voltage (V)','vlg':'LG voltage (V)','vbg':'BG voltage (V)','RF_frequency':'RF frequency (MHz)', 'RFgate_frequency':'RF gate frequency (MHz)','RF_power':'RF power (dBm)', 'RFgate_power':'RF gate power (dBm)','nothing':'Nothing'}

#set y variable
yvarname = 'RF_frequency' # 'vlg' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if yvarname not in coordinate_names:
    sys.exit('Aborted: yvarname not in coordinate_names')
y_start = 100
y_stop = 200
y_step = 10
if yvarname == 'nothing':
    y_stop=y_start
    Noysteps=1
else:
    Noysteps = round((y_stop-y_start)/y_step + 1)

#set z variable
zvarname = 'nothing' # 'vlg' or 'RF_power' or 'f_LO' or 'Vdd' or 'tc'
if zvarname not in coordinate_names:
    sys.exit('Aborted: zvarname not in coordinate_names')
z_start = -15
z_stop = -5
z_step = 5
if zvarname == 'nothing':
    z_start=1
    Nozsteps=1
    z_stop = Nozsteps
else:
    Nozsteps = abs(round((z_stop-z_start)/z_step) + 1)

#set fixed values

if (yvarname != 'vug') & (zvarname != 'vug'):
    vug_fixed = 0 #V
    ramp(vi,'vug',vug_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage offset: %sV +++' % vug_fixed

if (yvarname != 'vlg') & (zvarname != 'vlg'):
    vlg_fixed = 0 #V
    vlg=vlg_fixed
    ramp(vi,'vlg',vlg_fixed,sweepstep,sweeptime)
    print '+++ Gate voltage: %sV +++' % vlg_fixed

if (yvarname != 'vbg') & (zvarname != 'vbg'):
    vbg_fixed=0 #V
    ramp(vi,'vbg',vbg_fixed,sweepstep,sweeptime)
    print '+++ Bias voltage: %sV +++' % vbg_fixed    

if (yvarname != 'RF_frequency') & (zvarname != 'RF_frequency'):
    RF_frequency=102 #MHz
    smb.set_RF_frequency(RF_frequency)
    print '+++ RF frequency: %sMHz +++' % RF_frequency

if (yvarname != 'RFgate_frequency') & (zvarname != 'RFgate_frequency'):
    RFgate_frequency=101 #MHz
    smbgate.set_RF_frequency(RFgate_frequency)
    print '+++ RF gate frequency: %sMHz +++' % RFgate_frequency    

if (yvarname != 'RF_power') & (zvarname != 'RF_power'):
    RF_power=-10 #dBm (Currently with 10dB in attenuation)   
    smb.set_RF_power(RF_power)
    print '+++ RF power: %sdBm +++' % RF_power
else:
    smb.set_RF_power(-70) 

if (yvarname != 'RFgate_power') & (zvarname != 'RFgate_power'):
    RFgate_power=0 #dBm (Currently with 10dB in attenuation)   
    smbgate.set_RF_power(RFgate_power)
    print '+++ RF gate power: %sdBm +++' % RFgate_power
else:
    smb.set_RF_power(-70)    


#set filename
filename='Katsus_device_spectrum_vs_'+yvarname+'_and_'+zvarname
    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vlg()

#ready the smb
smb.set_RF_state(True)    
smbgate.set_RF_state(True)

smbgate.set_reference('INT')
smb.set_reference('EXT')
smbgate.get_all()
    
#ready the fsl

fsl.set_trace_continuous(True)
fsl.set_filter_type('FFT') #use 'NORM' above 30 kHz
fsl.set_trace_mode('AVER')
fsl.set_number_of_sweeps(30000)
bandwidth = 0.11 # MHz
fsl.set_resolution_bandwidth(bandwidth) #MHz

queryingtime = 0.2 # don't use lower because has not "settled"
NoAverages = 1  

span = RF_stop_fixed-RF_start_fixed
fsl.set_sweeppoints(NoRFsteps)
fsl.set_span(span)    
fstep=span/(NoRFsteps-1.0)

RF_center = (RF_stop_fixed+RF_start_fixed)/2   
fsl.set_center_frequency(RF_center)

#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('Frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])
data.add_value('Power (dBm)')
    
data.create_file()
data.copy_file('Katsu_ND_frequency_trace.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep

for zvar in linspace(z_start,z_stop,Nozsteps):
    #set z variable
    if zvarname == 'vug':
        ramp(vi,'vug',zvar,sweepstep,sweeptime)
    elif zvarname == 'vlg':
        vlg = zvar
        ramp(vi,'vlg',zvar,sweepstep,sweeptime)
    elif zvarname == 'vbg':
        ramp(vi,'vbg',zvar,sweepstep,sweeptime)
    elif zvarname == 'RF_frequency':
        smb.set_RF_frequency(zvar)
    elif zvarname == 'RFgate_frequency':
        smbgate.set_RF_frequency(zvar)                    
    elif zvarname == 'RF_power':
        smb.set_RF_power(zvar)        
    elif zvarname == 'RFgate_power':
        smbgate.set_RF_power(zvar)

    z_array=zvar*ones(NoRFsteps)
    
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    
    
    for yvar in linspace(y_start,y_stop,Noysteps):
        #set y variable
        if yvarname == 'vug':
            ramp(vi,'vug',yvar,sweepstep,sweeptime)
        elif yvarname == 'vlg':
            vlg = yvar
            ramp(vi,'vlg',yvar,sweepstep,sweeptime)
        elif yvarname == 'vbg':
            ramp(vi,'vbg',yvar,sweepstep,sweeptime)
        elif yvarname == 'RF_frequency':
            smb.set_RF_frequency(yvar)
        elif yvarname == 'RFgate_frequency':
            smbgate.set_RF_frequency(yvar)                                
        elif yvarname == 'RF_power':
            smb.set_RF_power(yvar)
        elif yvarname == 'RFgate_power':
            smbgate.set_RF_power(yvar)
            
        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar

        y_array=zvar*ones(NoRFsteps)
            

        qt.msleep(.1)
      
        fsl.initiate()
        currentsweepnumber=0
        while currentsweepnumber <= NoAverages:
            print currentsweepnumber
            qt.msleep(queryingtime)
            currentsweepnumber =fsl.get_current_sweep_number()
            
        print 'passed'

        power=fsl.grab_trace() #actual measurement

        print 'passed2'
        
        data.add_data_point(RF_array_fixed,y_array,z_array,power)

        data.new_block()

        if displayintermediatetime:
            deltatime = time()-inttime
            totaltime = deltatime*Noysteps*Nozsteps
            inttime = time()
            intmeasurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((inttime-begintime)/3600),"m":int(((inttime-begintime)%3600)/60),"s":int(((inttime-begintime)%3600)%60)}
            totalmeasurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((totaltime)/3600),"m":int(((totaltime)%3600)/60),"s":int(((totaltime)%3600)%60)}
            print 'Current measurement time: '+ intmeasurementtimestring
            print 'Estimated total measurement time: '+ totalmeasurementtimestring

    spyview_process(data,RF_stop_fixed,RF_start_fixed,y_start,y_stop,zvar)    
    

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)
plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')

#reset voltages
if returntozero:
    ramp(vi,'vug',0,sweepstep,sweeptime)
    ramp(vi,'vlg',0,sweepstep,sweeptime)
    ramp(vi,'vbg',0,sweepstep,sweeptime)

print 'UG voltage: %sV' % vi.get_vug()
print 'LG voltage: %sV' % vi.get_vlg()
print 'BG voltage: %sV' % vi.get_vbg()

smbgate.set_RF_state(False)
smb.set_RF_state(False)
          

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}
print 'Measurement time: '+ measurementtimestring

data.close_file()

qt.mend()
