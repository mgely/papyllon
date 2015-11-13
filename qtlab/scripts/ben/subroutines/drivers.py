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
            
    if highfrequency:
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

        if IVVIactivate:
                # was used for IVVI
                vi.add_variable_scaled('vgatefine',ivvi,'dac2',10*1000,0.0) #0.1x modulation
                vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
                vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
                vi.add_variable_scaled('vdd',ivvi,'dac7',1000,0.0)
                if useattenuators:
                    vi.add_variable_scaled('vattplus',ivvi,'dac2',1,0.0)
                    vi.add_variable_scaled('vattctrl',ivvi,'dac3',1,0.0)

                if externality == 'RFswitch':
                    vi.add_variable_scaled('vRFplus',lockin,'out1',1,0.0)
                    vi.add_variable_scaled('vRFminus',lockin,'out2',1,0.0)

        else:
                vi.add_variable_scaled('vgate',lockin,'out1',1,0.0) #because ivvi.set_dac is in mV
                vi.add_variable_scaled('vgatefine',lockin,'out2',10,0.0) #0.1x modulation
                vi.add_variable_scaled('vbias',lockin,'out3',10,0.0)
                vi.add_variable_scaled('vdd',lockin,'out4',1,0.0)
                if useattenuators:
                    vi.add_variable_scaled('vattplus',lockin,'out2',1,0.0)
                    vi.add_variable_scaled('vattctrl',lockin,'out1',1,0.0)

                if externality == 'RFswitch':
                    HFlockin.set_auxmode(2,-1)  #sets aux 3 to manual
                    HFlockin.set_auxmode(3,-1)  #sets aux 4 to manual
                    vi.add_variable_scaled('vRFplus',HFlockin,'auxoffset2',1,0.0)
                    vi.add_variable_scaled('vRFminus',HFlockin,'auxoffset3',1,0.0)
                    

        
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
