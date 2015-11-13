    if zvarname == 'vgatefine':
        ramp(vi,'vgatefine',zvar,sweepstep,sweeptime)
    elif zvarname == 'vgate':
        vgate = zvar
        ramp(vi,'vgate',zvar,sweepstep,sweeptime)
    elif zvarname == 'vbias':
        ramp(vi,'vbias',zvar,sweepstep,sweeptime)        
    elif zvarname == 'RF_power':
        smb.set_RF_power(zvar)
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
            HFoscil.set_time_scale(20e-6)
            #HFoscil.set_time_scale(timeconstant)
    elif zvarname == 'Vdd':
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

    if (readoutmode == 'oscilloscope')|(readoutmode == 'HFoscil'):
        z_array=zvar*ones(Notimesteps)
    else:
        z_array=zvar*ones(NoRFsteps)
