awg = qt.instruments.create('awg','Tektronix_AWG520',address='GPIB::1::INSTR')


awg.send_waveform(sinwave,marker1,marker2,'testwave1.pat',1000000000)
awg.get_clock()
marker1 = np.linspace(1,1,4000000)
awg.get_numpoints()

awg.get_ch1_amplitude()
wave = np.sin(numpoints)
wave = np.sin(numpoints)
marker1 = np.linspace(1,1,4000000)
marker2 = np.linspace(1,1,4000000)
awg.send_waveform(sinwave,marker1,marker2,'testwave1.pat',1000000000)