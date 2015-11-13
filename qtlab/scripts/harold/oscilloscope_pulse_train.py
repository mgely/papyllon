import qt
import sys
from time import time
import numpy as np
execfile('ramp.py')
execfile('metagen3D.py')

begintime = time() #for measurement time calculation
highfrequency = True #measure with HFlockin (Zurich Instruments) and use HEMT (set Vdd)?
returntozero = True #sweep voltages back to zero?

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

  
if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'vi' not in instlist:
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgate',lockin,'out1',1,0.0)
    vi.add_variable_scaled('vbias',lockin,'out2',10,0.0)
    vi.add_variable_scaled('vdd',lockin,'out3',1,0.0)

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

if 'smbpulse' not in instlist:
    smbpulse = qt.instruments.create('smbpulse','RS_SMB100A',address='GPIB::30::INSTR')

if 'oscil' not in instlist:
    oscil = qt.instruments.create('oscil','Rigol_DS1102E',address='USB0::0x1AB1::0x0588::DS1EB122904339::INSTR')

#measurement information
med.set_temperature(300)
med.set_device('lg-04xx31b2')
med.set_setup('1K dipstick')
med.set_user('Harold')
current_gain = 0.001 #GV/A=mV/pA
#med.set_current_gain(current_gain)

#set frequencies
RF_fixed=200 #MHz

#how many prints on screen per loop
if NoRFsteps > 10:
    NoPrints = 10
else:
    NoPrints = 2


#set fixed values
#vbias_fixed=0.001 #V

vgate_fixed = 3.5 #V
ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
print '+++ Gate voltage: %sV +++' % vgate_fixed

RF_voltage= 1 #V (Currently with 10dB in attenuation before source)
HFlockin.set_power0(RF_voltage)
print '+++ RF voltage: %sV +++' % RF_voltage

RFgate_power=10 #dBm (Currently with 20dB in attenuation)   
smbgate.set_RF_power(RFgate_power)
print '+++ RF gate power: %sdBm +++' % RFgate_power

LO_frequency= 45997.0 #997.0 #kHz
HFlockin.set_frequency0(LO_frequency*1000)
print '+++ LO frequency: %skHz +++' % LO_frequency

Vdd_fixed = 1 #V
ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
print '+++ Vdd: %sV +++' % Vdd_fixed


#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)

#set filename
filename='lg-04xx31b2_oscilloscope_pulse_train'
    
qt.mstart()

#ready the lockin
lockin.get_all()
vi.get_vgate()

#ready the oscilloscope



#ready the smb
smbgate.set_RF_state(True)
smbgate.set_reference('INT')
smbgate.get_all()

sys.exit()
#Set up datafile
data = qt.Data(name=filename)
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_coordinate(coordinate_names[zvarname])

if scalarsubtractbackground & (yvarname != 'vgate'):
    data.add_value('R_subtracted (V)')
    data.add_value('R_ref (V)')
                    
if highfrequency:
    data.add_value('R (V)')
    data.add_value('theta (rad)')
    data.add_value('X (V)')
    data.add_value('Y (V)')
    data.add_value('DC (pA)')
else:
    data.add_value('R (V)')
    data.add_value('theta (rad)')
    data.add_value('X (pA)')
    data.add_value('Y (pA)')
    data.add_value('DC (pA)')
    
data.create_file()
data.copy_file('3D_twosource_mixed_sweep.py')

#initialize spyview meta.txt file
spyview_process(reset=True)

#Actual sweep

for zvar in linspace(z_start,z_stop,Nozsteps):


    #set z variable
    if zvarname == 'vgate':
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'RF_power':
        smb.set_RF_power(zvar)
    elif zvarname == 'RFgate_power':
        smbgate.set_RF_power(zvar)
    elif zvarname == 'f_LO':
        LO_frequency=zvar
        HFlockin.set_frequency0(LO_frequency*1000)
    elif zvarname == 'tc':
        vartimeconstant=10**zvar
        HFlockin.set_timeconstant0(vartimeconstant)
        settlingtime = 10*vartimeconstant#s used for wait time, should exceed 50 ms?
    elif zvarname == 'Vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)
    elif zvarname == 'sweepdirection':
        if zvar == 1:
            RF_start = RF_start_fixed
            RF_stop = RF_stop_fixed
        elif zvar == -1:
            RF_start = RF_stop_fixed
            RF_stop = RF_start_fixed            
    z_array=zvar*ones(NoRFsteps)
    
    print '<<< '+ coordinate_names[zvarname] + ': %s >>>' % zvar    
    
    for yvar in linspace(y_start,y_stop,Noysteps):
        #set y variable
        if yvarname == 'vgate':
            ramp(vi,'vgate',yvar,sweepstep,sweeptime)
        elif yvarname == 'RF_power':
            smb.set_RF_power(yvar)
        elif yvarname == 'RFgate_power':
            smbgate.set_RF_power(yvar)
        elif yvarname == 'f_LO':
            LO_frequency=yvar
            HFlockin.set_frequency0(LO_frequency*1000)
        elif yvarname == 'tc':
            vartimeconstant = 10**yvar
            HFlockin.set_timeconstant0(vartimeconstant)
            settlingtime = 10*vartimeconstant #s used for wait time, should exceed 50 ms?
        elif yvarname == 'Vdd':
            ramp(vi,'vdd',yvar,sweepstep,sweeptime)        
        elif yvarname == 'sweepdirection':
            if yvar == 1:
                RF_start = RF_start_fixed
                RF_stop = RF_stop_fixed
            elif yvar == -1:
                RF_start = RF_stop_fixed
                RF_stop = RF_start_fixed          

        print '=== '+ coordinate_names[yvarname] + ': %s ===' % yvar

        y_array=yvar*ones(NoRFsteps)
        qt.msleep(.2)

        #scalar subtraction of background (unavailable if gate voltage is looped)
        if scalarsubtractbackground & (yvarname != 'vgate'):
            x_ref=zeros(NoRFsteps)
            y_ref=zeros(NoRFsteps)
            r_ref=zeros(NoRFsteps)

            ramp(vi,'vgate',vgate_ref,sweepstep,sweeptime)
            print 'getting background reference trace'

            counter = 0
            for f in linspace(RF_start,RF_stop,NoRFsteps):
                smbgate.set_RF_frequency(f)
                qt.msleep(settlingtime)
                    
                if highfrequency:
                    x_ref[counter]=HFlockin.get_x()
                    y_ref[counter]=HFlockin.get_y()
                    r_ref[counter]=HFlockin.get_amplitude()
                else:
                    rawdat=lockin.query('SNAP?1,2')
                    datlist=rawdat.split(',')
                    x_ref[counter]=1e12*float(datlist[0])
                    y_ref[counter]=1e12*float(datlist[1])
                    r_ref[counter]=sqrt((x_ref[counter])**2+(y_ref[counter])**2)

                counter=counter+1        
            ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)

        #measure dc current    
        if recorddc:
            i=vm.get_readval()/current_gain*-1e3
        else:
            i=0
        i_array = i*ones(NoRFsteps)

            
        #measure forward sweep      
        
        x=zeros(NoRFsteps)
        y=zeros(NoRFsteps)
        r=zeros(NoRFsteps)
        theta=zeros(NoRFsteps)
        
        counter = 0
        
        for f in linspace(RF_start,RF_stop,NoRFsteps):
            smbgate.set_RF_frequency(f)
            qt.msleep(settlingtime)
                
            if highfrequency:
                x[counter]=HFlockin.get_x()
                y[counter]=HFlockin.get_y()
                r[counter]=HFlockin.get_amplitude()
                theta[counter] = HFlockin.get_phase()
            else:
                rawdat=lockin.query('SNAP?1,2')
                datlist=rawdat.split(',')
                x[counter]=1e12*float(datlist[0])
                y[counter]=1e12*float(datlist[1])
                r[counter]=sqrt(x[counter]**2+y[counter]**2)
                theta[counter]=arctan(y[counter]/x[counter])
                
            if scalarsubtractbackground & (yvarname != 'vgate'):
                r_subtracted = r-r_ref

            if counter%int(((RF_stop+RF_step-RF_start)/RF_step+1)/(NoPrints-1))==0:
                print 'RF frequency: %sMHz' % f
            counter=counter+1

        #save data
        if ((yvarname == 'sweepdirection') & (yvar==-1)) | ((zvarname == 'sweepdirection') & (zvar==-1)):
            r = np.flipud(r)
            theta = np.flipud(theta)
            x = np.flipud(x)
            y = np.flipud(y)
            if scalarsubtractbackground & (yvarname != 'vgate'):
                r_subtracted = np.flipud(r_subtracted)
                r_ref= np.flipud(r_ref)


        if scalarsubtractbackground & (yvarname != 'vgate'):
            data.add_data_point(RF_array_fixed,y_array,z_array,r_subtracted,r_ref,r,theta,x,y,i_array)
        else:    
            data.add_data_point(RF_array_fixed,y_array,z_array,r,theta,x,y,i_array)

        data.new_block()

    spyview_process(data,RF_stop,RF_start,y_start,y_stop,zvar)    
    

plot2dx = qt.Plot2D(data, name='xcomp', coorddim=0, valdim=3)
plot3Dx = qt.Plot3D(data, name='x3d', coorddims=(0,1), valdim=3)
plot2dx.save_png(filepath=data.get_dir()+'\\'+'plot2dx.png')
plot3Dx.save_png(filepath=data.get_dir()+'\\'+'plot3Dx.png')


#reset voltages
if returntozero:
    ramp(vi,'vgate',0,sweepstep,sweeptime)
    ramp(vi,'vbias',0,sweepstep,sweeptime)
    if highfrequency:
        ramp(vi,'vdd',0,sweepstep,sweeptime)

print 'Gate voltage: %sV' % vi.get_vgate()
print 'Vdd: %sV' % vi.get_vdd()

smbgate.set_RF_state(False)
if recorddc:
    vm.set_trigger_continuous(True)
                    

#record measurement time
endtime = time()
measurementtimestring = '%(h)s:%(m)s:%(s)s'% {"h":int((endtime-begintime)/3600),"m":int(((endtime-begintime)%3600)/60),"s":int(((endtime-begintime)%3600)%60)}

print 'Measurement time: '+ measurementtimestring

data.close_file()

qt.mend()
