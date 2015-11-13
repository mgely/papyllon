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
