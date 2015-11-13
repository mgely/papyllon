#setup two windows
pna.reset()
pna.w("DISP:WIND1:STATE ON")
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.w("DISP:WIND1:TRACE1:FEED 'CH1_S21_S1'")
pna.w("TRIG:SOUR EXT") #set trig to ext
pna.w("TRIG:TYPE EDGE") #set to trig on edge
pna.w("TRIG:SLOP POS") #pos edge trig
pna.w("SENS:SWE:TYPE CW") #Set CW type


smb.get_all()
smb.set_reference('EXT')
pulse_width = 500
pulse_period = 2000
smb.set_pulse_period(pulse_period) #us
smb.set_pulse_width(pulse_width) #us
smb.set_pulse_state(True)
smb.set_RF_state(False)

#pna.w('SENS:FREQ 5e9') #set CW fixed Freq
#pna.set_resolution_bandwidth(1e6) #IF bw in Hz
#pna.set_sweeptime() #Sweeptime in sec

#Triger delay
#pna.w("TRIG:DEL .0003")
#pna.q("TRIGger:DELay?")


