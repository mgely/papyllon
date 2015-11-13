#oscil = qt.instruments.create('oscil','Rigol_DS1102E',address='USB0::0x1AB1::0x0588::DS1EB122904339::INSTR')
#oscil.set_waveform_mode('RAW') #'RAW' or 'NORMAL'
#oscil.set_memory_depth('NORMAL') #'LONG' or 'NORMAL'
#qt.msleep(1)
#print oscil.get_waveform_mode()
#print oscil.get_memory_depth()

#oscil.set_time_scale(5e-9)


drivemode = 'external_mixer'
readoutmode = 'oscilloscope'
yvarname = 'nothing'
zvarname = 'nothing'

filename='lg-04xx31b2_'+drivemode+'_'+readoutmode+'_vs_'+yvarname+'_and_'+zvarname

data = qt.Data(name=filename)
data.add_coordinate('Time (s)')
data.add_coordinate('RF frequency (MHz)')
data.add_coordinate(coordinate_names[yvarname])
data.add_value('Channel 1 voltage (V)')
data.add_value('Channel 2 voltage (V)')

data.create_file()

spyview_process(reset=True)

#oscil.run()
#qt.msleep(0.1)
#oscil.stop()
#time, amplitude = oscil.get_trace('CHAN1')
#time2, amplitude2 = oscil.get_trace('CHAN2')
#plt.clear()

y_whitespace=(max(amplitude)-min(amplitude))*0.2
maxlen=260000
if len(time2)>abs(maxlen):
    plt = plot(time2[0:maxlen],amplitude[0:maxlen],title='CHAN1')
    plt = plot(time2[0:maxlen],amplitude2[0:maxlen],title='CHAN2')
    plt.set_xrange(time[0],time[maxlen])
    plt.set_yrange(min([min(amplitude),min(amplitude2)])-y_whitespace,max([max(amplitude),max(amplitude2)])+y_whitespace)
else:
    plt = plot(time2,amplitude,title='CHAN1')
    plt = plot(time2,amplitude2,title='CHAN2')
    plt.set_xrange(min(time2),max(time2))
    plt.set_yrange(min([min(amplitude),min(amplitude2)])-y_whitespace,max([max(amplitude),max(amplitude2)])+y_whitespace)

plt.set_xlog(False)

    


plt.set_xlabel('Time (s)')
plt.set_ylabel('Voltage (V)')



time_array = time2
RF_array_fixed = 200*ones(len(time2))
y_array = ones(len(time2))
amplitude_array = amplitude
amplitude2_array = amplitude2



data.add_data_point(time_array, RF_array_fixed,y_array,amplitude_array,amplitude2_array)
data.new_block()


RF_start = 200
RF_stop = 200
yvar = 1
spyview_process(data,min(time_array),max(time_array),RF_start,RF_stop,yvar)

data.close_file()
