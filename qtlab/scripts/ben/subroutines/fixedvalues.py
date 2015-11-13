def set_fixed_values(yvarname,zvarname,RF_start_fixed,RF_stop_fixed,vgatefine_fixed = 0,vgate_fixed = 0,vbias_fixed=0.010,RF_voltage= 1,RF_power=0,RFgate_power=0,LO_frequency= 5997.0,logtimeconstant = -4,Vdd_fixed = 1,Vattplus= 0,Vattctrl= 0, **kwargs):
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

    if (yvarname != 'Vdd') & (zvarname != 'Vdd'):
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
        smb.set_pulse_state(False)
        smb.set_pulse_period(1000) #us
        smb.set_pulse_width(500) #us
        
    if (yvarname != 'sweepdirection') & (zvarname != 'sweepdirection'):
        global RF_start
        global RF_stop
        RF_start = RF_start_fixed #not returning this via prototype yet
        RF_stop = RF_stop_fixed
    print '+++ Sweep direction: forward +++'
