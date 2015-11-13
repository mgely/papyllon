import qt
import sys
from time import time
import numpy
execfile('ramp.py')

#load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

drivemode = 'external_mixer'

# drivemode:
#'direct_source': use signal generator on source, measure at drive frequency,
#'direct_gate': use signal generator on gate, measure at drive frequency,
#'external_mixer': use smbgate signal generator and externally mixed with lockin ref out,
#'two-source': use two signal generators
#'two-source_noise': use smb on source to probe, measure noise at difference frequency
#'AM_gate': amplitudemodulation on gate
#'undriven': no signal generators used

mixed_drivemode = (drivemode=='external_mixer')|(drivemode=='two-source')|(drivemode=='AM_gate')
direct_drivemode = (drivemode=='direct_source')|(drivemode=='direct_gate')

readoutmode = 'HFlockin'
#readoutmode='HFlockin','LFlockin','spectrum_analyzer','none' (dc only),'oscilloscope'

externality = 'RFswitch'
#'RFswitch','attenuator' (not programmed yet)  

if readoutmode == 'oscilloscope':
    oscil = qt.instruments.create('oscil','Rigol_DS1102E',address='USB0::0x1AB1::0x0588::DS1EB122904339::INSTR')

if readoutmode=='HFlockin':
    if 'HFlockin' not in instlist:
        HFlockin = qt.instruments.create('HFlockin', 'ZI_HF_2LI',host='localhost',port=8005,reset=False)

if readoutmode == 'spectrum_analyzer':
    if 'fsl' not in instlist:
        fsl = qt.instruments.create('fsl','RS_FSL',address='GPIB::22::INSTR')
    
if 'lockin' not in instlist:
    lockin = qt.instruments.create('lockin','SR830',address='GPIB::9')

if 'ivvi' not in instlist:
    ivvi = qt.instruments.create('ivvi','Optodac',address='COM1')
    ivvi.set_dac_range(3,10000) #uses altered Optodac.py

if False | ('vi' not in instlist):
    vi = qt.instruments.create('vi','virtual_composite')
    vi.add_variable_scaled('vgatefine',ivvi,'dac2',10*1000,0.0) #0.1x modulation
    vi.add_variable_scaled('vgate',ivvi,'dac3',1000,0.0) #because ivvi.set_dac is in mV
    vi.add_variable_scaled('vbias',ivvi,'dac5',10*1000,0.0)
    vi.add_variable_scaled('vdd',ivvi,'dac7',1000,0.0)
    if externality == 'attenuator':
        vi.add_variable_scaled('vattplus',ivvi,'dac2',1,0.0)
        vi.add_variable_scaled('vattctrl',ivvi,'dac3',1,0.0)
    if externality == 'RFswitch':
        vi.add_variable_scaled('vRFplus',lockin,'out1',1,0.0)
        vi.add_variable_scaled('vRFminus',lockin,'out2',1,0.0)
    

if False | (('vm' not in instlist)):
    vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'smbgate' not in instlist:
    smbgate = qt.instruments.create('smbgate','RS_SMB100A',address='GPIB::28::INSTR')

if False | ('smb' not in instlist):
    smb = qt.instruments.create('smb','RS_SMB100A',address='GPIB::29::INSTR')

if False:
    if 'tempcon' not in instlist:
        tempcon = qt.instruments.create('tempcon','Lakeshore_331',address='GPIB::12')

#voltage ramp settings
sweepstep=.01#V
sweeptime=.01#(s) (up to max speed of ~5ms)
