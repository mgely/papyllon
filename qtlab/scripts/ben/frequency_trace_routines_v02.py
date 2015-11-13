import qt
import numpy as np
import time as timemod

#load instrument plugins
def install_drivers(instlist,
    readoutmode = 'HFlockin',
    highfrequency = True,
    externality = 'nothing',
    IVVIactivate = False):
    
    if readoutmode == 'oscilloscope':
        global oscil
        oscil = qt.instruments.create('oscil','Rigol_DS1102E',address='USB0::0x1AB1::0x0588::DS1EB122904339::INSTR')
        
    if False | ('HFoscil' not in instlist):
        if readoutmode == 'HFoscil':
            global HFoscil
            HFoscil = qt.instruments.create('HFoscil','RS_RTO_1014',address='TCPIP0::192.168.100.101::inst0::INSTR')
            
    #if highfrequency:
    if 'HFlockin' not in instlist:
        global HFlockin
        HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)
        
    #if 'fsl' not in instlist:
    #    fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')
        
    if 'lockin' not in instlist:
        global lockin
        lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

    if IVVIactivate:
        if 'ivvi' not in instlist:
            global ivvi
            ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
            ivvi.set_dac_range(3,10000) #uses altered Optodac.py

    if False | ('vi' not in instlist):
        global vi
        vi = qt.instruments.create('vi','virtual_composite')
        HFlockin.set_auxmode(2,-1)  #sets aux 3 to manual
        HFlockin.set_auxmode(3,-1)  #sets aux 4 to manual
        vi.add_variable_scaled('vgate',HFlockin,'auxoffset2',1,0.0)
        vi.add_variable_scaled('vbias',HFlockin,'auxoffset3',5*100,0.0) #use 5 to 1 Volt devider [old:use voltage devider(9.253 to 1)] and 10mV bias setting #10mV/1V 1V/10V -> 10mV/10V
        vi.add_variable_scaled('vgatefine',lockin,'out2',10,0.0) #0.1x modulation
        vi.add_variable_scaled('vdd',lockin,'out1',1,0.0)
        vi.add_variable_scaled('vRFplus',lockin,'out4',1,0.0) #because ivvi.set_dac is in mV
        vi.add_variable_scaled('vRFminus',lockin,'out3',1,0.0)

                    

        
    if False | (('vm' not in instlist) and recorddc):
        global vm
        vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

    if 'med' not in instlist:
        global med
        med = qt.instruments.create('med','med')

    if 'smbgate' not in instlist:
        global smbgate
        smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

    if False | ('smb' not in instlist):
        global smb
        smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')

    if 'tempcon' not in instlist:
        global tempcon
        tempcon = qt.instruments.create('tempcon','Lakeshore_331',address='GPIB::12')

def set_fixed_values(yvarname,zvarname,RF_start_fixed,RF_stop_fixed,vgatefine_fixed = 0,vgate_fixed = 0,vbias_fixed=0.010,RF_voltage= 1,RF_power=0,RFgate_power=0,LO_frequency= 5997.0,logtimeconstant = -3,Vdd_fixed = 0.4,Vattplus= 0,Vattctrl= 0, **kwargs):
    '''
    all values should be in Voltage or dBm, logtimeconstant is
    log10(780e-9) #minimum: 780ns ~ 10**(-6.1)
            timeconstant = 10**logtimeconstant
    '''
    if (yvarname != 'vgatefine') & (zvarname != 'vgatefine'):
        ramp(vi,'vgatefine',vgatefine_fixed,sweepstep,sweeptime)
        print '+++ Gate voltage offset: %sV +++' % vgatefine_fixed

    if (yvarname != 'vgate') & (zvarname != 'vgate'):
        #V
        global vgate
        vgate=vgate_fixed
        ramp(vi,'vgate',vgate_fixed,sweepstep,sweeptime)
        print '+++ Gate voltage: %sV +++' % vgate_fixed

    if (yvarname != 'vbias') & (zvarname != 'vbias'):
         #V
        ramp(vi,'vbias',vbias_fixed,sweepstep,sweeptime)
        print '+++ Bias voltage: %sV +++' % vbias_fixed    

    if (yvarname != 'RF_voltage') & (zvarname != 'RF_voltage'):
         #V (Currently with 10dB in attenuation before source)
        HFlockin.set_power0(RF_voltage)
        print '+++ RF voltage: %sV +++' % RF_voltage
    else:
        HFlockin.set_power0(0)    

    if (yvarname != 'RF_power') & (zvarname != 'RF_power'):
         #dBm (Currently with 10dB in attenuation)   
        smb.set_RF_power(RF_power)
        print '+++ RF power: %sdBm +++' % RF_power
    else:
        smb.set_RF_power(-70) 

    if (yvarname != 'RFgate_power') & (zvarname != 'RFgate_power'):
        #dBm (Currently with 10dB in attenuation)   
        smbgate.set_RF_power(RFgate_power)
        print '+++ RF gate power: %sdBm +++' % RFgate_power
    else:
        smb.set_RF_power(-70)    

    if (yvarname != 'f_LO') & (zvarname != 'f_LO'):
         #997.0 #kHz
        HFlockin.set_frequency0(LO_frequency*1000)
        print '+++ LO frequency: %skHz +++' % LO_frequency

    if (yvarname != 'tc') & (zvarname != 'tc'):
        # log10(780e-9) #minimum: 780ns ~ 10**(-6.1)
        global timeconstant
        timeconstant = 10**logtimeconstant
        HFlockin.set_timeconstant0(timeconstant) #timeconstant_fixed
        global settlingtime
        settlingtime = 10*timeconstant #s used for wait time, should exceed 50 ms?
        if readoutmode == 'oscilloscope':
            oscil.set_time_scale(timeconstant)
        elif readoutmode == 'HFoscil':
            HFoscil.set_time_scale(10*timeconstant)        
        print '+++ timeconstant: %ss +++' % timeconstant

    if (yvarname != 'vdd') & (zvarname != 'vdd'):
         # 1 V @ RT, 0.5 V @ 77K
        ramp(vi,'vdd',Vdd_fixed,sweepstep,sweeptime)
        print '+++ Vdd: %sV +++' % Vdd_fixed

    if useattenuators:
        if (yvarname != 'Vattplus') & (zvarname != 'Vattplus'):
            #4999 #mV
            vi.set_vattplus(Vattplus)
            print '+++ Attenuator Voltage+: %sV +++' % Vattplus

        if (yvarname != 'Vattctrl') & (zvarname != 'Vattctrl'):
            #5000 #mV
            vi.set_vattctrl(Vattctrl)
            print '+++ Attenuator Voltage+: %sV +++' % Vattctrl
    
    if externality == 'RFswitch':
        vi.set_vRFplus(5)
        vi.set_vRFminus(-5)
        #smb.set_pulse_state(False)
        #smb.set_pulse_period(3000) #us
        #smb.set_pulse_width(1000) #us
        
#    if (yvarname != 'sweepdirection') & (zvarname != 'sweepdirection'):
#        global RF_start
#        global RF_stop
#        RF_start = RF_start_fixed #not returning this via prototype yet
#        RF_stop = RF_stop_fixed
#    print '+++ Sweep direction: forward +++'

def sweep_vars(zvarname,zvar,sweepsetp,sweeptime):
    #set a variable
    if zvarname == 'vgatefine':
        ramp(vi,'vgatefine',zvar,sweepstep,sweeptime)
    elif zvarname == 'vgate':
        global vgate
        vgate = zvar
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'vbias':
        ramp(vi,'vbias',zvar,sweepstep,sweeptime)        
    elif zvarname == 'RF_power':
        smb.set_RF_power(zvar)
    elif zvarname == 'RFgate_power':
        smbgate.set_RF_power(zvar)
    elif zvarname == 'f_LO':
        LO_frequency=zvar
        if usetwosourcemixing:
            smbgate.set_RF_frequency(RF_start)
            smb.set_RF_frequency(RF_start+LO_frequency/1000)
        else:
            HFlockin.set_frequency0(LO_frequency*1000)
    elif zvarname == 'tc':
        timeconstant=10**zvar
        HFlockin.set_timeconstant0(timeconstant)
        settlingtime = 10*timeconstant#s used for wait time, should exceed 50 ms?
        if readoutmode == 'oscilloscope':
            oscil.set_time_scale(timeconstant)
        elif readoutmode == 'HFoscil':
            HFoscil.set_time_scale(150e-6)
            #HFoscil.set_time_scale(timeconstant)
    elif zvarname == 'vdd':
        ramp(vi,'vdd',zvar,sweepstep,sweeptime)
    elif zvarname == 'sweepdirection':
        if zvar == 1:
            RF_start = RF_start_fixed
            RF_stop = RF_stop_fixed
        elif zvar == -1:
            RF_start = RF_stop_fixed
            RF_stop = RF_start_fixed
    elif zvarname == 'Vattplus':
        vi.set_vattplus(zvar)
    elif zvarname == 'Vattctrl':
        vi.set_vattctrl(zvar)

def ramp(instrument,parameter,value,step,time):
    '''
    instrument -- actual variable where instrument is stored
    parameter -- (string) parameter to be ramped. Must have get and set.
    value -- final value
    step -- stepsize
    time -- timestep Beware; don't set too small or the instrument can't keep up!
            In the case of some instruments (eg. SR830) not a problem
    '''
    start = timemod.time()
    
    v_start = getattr(instrument,'get_%s' % parameter)()

    if value>v_start:
        step=abs(step)
    else:
        step=-abs(step)

    if 2*abs(step)>abs(value-v_start):
        getattr(instrument,'set_%s' % parameter)(value)

    else:
        for v in np.arange(v_start,value,step):
            getattr(instrument,'set_%s' % parameter)(v)
            qt.msleep(time)
        getattr(instrument,'set_%s' % parameter)(value)

    qt.msleep(time)
    tc=timemod.time()-start
    #print('ramp complete in %s seconds' % tc)

def ramp_all_to_zero(instrument,step,time):
    for parameter in instrument.get_parameter_names():
        ramp(instrument,parameter,0,step,time)
        print parameter+': %sV'%instrument.get(parameter)


def spyview_process(data=0,len1=0,minval1=0,maxval1=0,len2=0,minval2=0,maxval2=0,len3=0,minval3=0,maxval3=0):
    '''
    Inteded to be simple and easily adjusted

    To be written in the meta file:
    example:
    '#loop1'
    len(f_list)
    f1_start
    f1_stop
    Frequency (Hz) #better get name from coordinate...
    '#loop2'
    len(g_list)
    gate_start
    gate_stop
    Gate [V]
    '#loop3'
    len(pow_list)
    pow_start
    f1_power
    Power [dBm]
    #values
    4
    S21 (Mlog) [dBm]]

    Substitute for "data.new_block"
    Creates spyview meta.txt file after every block is completed

    REQUIRED Arguments:
        data -- the data object
        len1 -- number points of inner loop
        minval1 -- minval of inner loop
        maxval1 -- maxval of inner loop
        len2 -- number pointsof outer loop
        minval2 -- minval of outer loop
        maxval2 -- maxval of outer loop
        len3
        minval3 -- minval of outermost loop
        maxval3 -- maxval of outermost loop
    '''
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
    #write down value names into meta file
    for i in range(3,len(data.get_dimensions()) ):
            dim_label=str(data.get_dimension_name(i))
            metafile.write('#values\n' + str(i+1) + '\n' + dim_label)

            
    '''
    testcommand:
    for i in range(4,len(data.get_dimensions())):
        print '#values\n',i,'\n',str(data.get_dimension_name(i)-1)

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
        metafile.write('#values\n'
                       +'9\n'
                       +str(data.get_dimension_name(8)))
    '''
    metafile.close()

